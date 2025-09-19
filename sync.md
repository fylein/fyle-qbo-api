# Fyle-QBO Attribute Synchronization Architecture

## Overview

This document outlines the current architecture for attribute synchronization between Fyle, the integration database, and QuickBooks Online (QBO). It also proposes a webhook-based architecture to replace the current polling-based system for Fyle attribute synchronization.

## Current Architecture Flows

### 1. Sync Fyle Dimensions Flow

The `sync_fyle_dimensions` function is responsible for importing/syncing attributes FROM Fyle TO the integration database.

```mermaid
graph TD
    A[sync_fyle_dimensions called] --> B{Check source_synced_at}
    B -->|Never synced OR > 24hrs| C[Create FyleCredential & PlatformConnector]
    B -->|Recently synced < 24hrs| Z[Skip sync]

    C --> D[platform.import_fyle_dimensions with taxes]
    D --> E[Sync Categories, Projects, Employees, etc.]
    E --> F[Count unmapped corporate cards]

    F --> G{CCC expenses object configured?}
    G -->|Yes| H[Call patch_integration_settings_for_unmapped_cards]
    G -->|No| I[Update workspace.source_synced_at]

    H --> I
    I --> J[End]

    subgraph "Called from"
        K[SyncFyleDimensionView POST API]
        L[RefreshFyleDimensionView POST API]
        M[Export chain __create_chain_and_run]
        N[Periodic sync tasks]
    end

    K --> A
    L --> A
    M --> A
    N --> A
```

**Key Points:**
- Triggered manually via API endpoints or automatically during exports
- Uses 24-hour interval check to avoid over-syncing
- Imports ALL Fyle dimensions (categories, projects, employees, etc.) to local DB
- Updates workspace.source_synced_at timestamp

### 2. Import Destination Attributes to Fyle Flow

This is the reverse flow - importing attributes FROM QBO TO Fyle when mapping settings are configured.

```mermaid
graph TD
    A[import_destination_attribute_to_fyle called] --> B[Get FyleCredential & PlatformConnector]
    B --> C[sync_expense_attributes - Sync FROM Fyle TO local DB]
    C --> D[sync_destination_attributes - Sync FROM QBO TO local DB]
    D --> E[construct_payload_and_import_to_fyle]

    E --> F[Get destination attributes with filters]
    F --> G{Any attributes to import?}
    G -->|No| H[Mark import log COMPLETE]
    G -->|Yes| I[Process in batches of 200]

    I --> J[For each batch:]
    J --> K[Remove duplicates]
    K --> L[Get existing Fyle attributes]
    L --> M[Construct Fyle payload]
    M --> N[Post to Fyle via platform connector]
    N --> O[Update import log progress]

    O --> P{Last batch?}
    P -->|No| J
    P -->|Yes| Q[sync_expense_attributes again]

    Q --> R[create_mappings between destination & Fyle]
    R --> S{Is Category with 3D mapping?}
    S -->|Yes| T[create_ccc_mappings]
    S -->|No| U[resolve_expense_attribute_errors]

    T --> U
    U --> V[End]

    subgraph "Trigger Sources"
        W[MappingSetting pre_save signal]
        X[MappingSetting post_save signal]
        Y[Scheduled import tasks]
        Z[trigger_import_via_schedule]
    end

    W --> A
    X --> A
    Y --> A
    Z --> A
```

**Key Points:**
- Triggered by mapping setting changes or scheduled tasks
- Syncs QBO attributes (accounts, items, classes, etc.) to Fyle
- Creates bidirectional mappings after import
- Processes in batches to handle large datasets
- Uses import logs to track progress and prevent duplicates

### 3. Mapping Settings and Trigger Flow

Shows how mapping settings control which attributes get imported to Fyle.

```mermaid
graph TD
    A[User configures Import Settings] --> B[ImportSettingsSerializer.update]
    B --> C[Update WorkspaceGeneralSettings]
    C --> D[Update MappingSettings]

    D --> E[MappingSetting pre_save signal]
    E --> F{import_to_fyle enabled?}
    F -->|Yes| G[Get import_log with -30min offset]
    F -->|No| P[Skip import]

    G --> H[Create module instance based on source_field]
    H --> I[Call expense_custom_field methods]
    I --> J[sync_expense_attributes]
    J --> K[construct_payload_and_import_to_fyle]
    K --> L[sync_expense_attributes again]

    L --> M[MappingSetting post_save signal]
    M --> N[schedule_or_delete_fyle_import_tasks]
    N --> O[Create/Delete scheduled import tasks]
    O --> P[End]

    subgraph "Module Classes"
        Q[Category - for ACCOUNT import]
        R[Project - for CLASS/CUSTOMER import]
        S[CostCenter - for DEPARTMENT import]
        T[ExpenseCustomField - for custom fields]
        U[Merchant - for VENDOR import]
    end

    H --> Q
    H --> R
    H --> S
    H --> T
    H --> U

    subgraph "Import Settings Examples"
        V[import_categories: true → ACCOUNT]
        W[import_projects: true → CLASS/CUSTOMER]
        X[Custom mapping: PROJECT → CLASS]
        Y[Custom mapping: COST_CENTER → DEPARTMENT]
    end
```

**Key Points:**
- Mapping settings determine which QBO attributes get imported to Fyle
- Different module classes handle different attribute types
- Pre/post save signals orchestrate the import process
- Scheduled tasks ensure regular syncing based on configuration

### 4. Current Webhook Infrastructure

Shows the existing webhook handling in the exports endpoint.

```mermaid
graph TD
    A[POST /workspaces/:id/fyle/exports/] --> B[ExportView.post]
    B --> C[async_import_and_export_expenses]
    C --> D{Check webhook action}

    D -->|ADMIN_APPROVED<br/>APPROVED<br/>STATE_CHANGE_PAYMENT_PROCESSING<br/>PAID| E[Extract report_id, org_id, state]
    D -->|ACCOUNTING_EXPORT_INITIATED| F[Extract report_id, org_id]
    D -->|UPDATED_AFTER_APPROVAL| G[Extract org_id]
    D -->|Other actions| H[No action]

    E --> I[Validate request with assert_valid_request]
    F --> J[Validate request]
    G --> K[Validate request]

    I --> L[Create payload for RabbitMQ]
    J --> M[Call import_and_export_expenses directly]
    K --> N[Call update_non_exported_expenses]

    L --> O[Publish to RabbitMQ EXPORT queue]
    O --> P[End]
    M --> P
    N --> P

    subgraph "Webhook Body Structure"
        Q[action: string<br/>data: object<br/>resource: string]
    end
```

**Key Points:**
- Single endpoint handles multiple webhook action types
- Currently handles expense/report related webhooks only
- Uses both direct async_task calls and RabbitMQ for processing
- Validates org_id matches workspace before processing

## Proposed Webhook-Based Architecture

### 1. Enhanced Webhook Handler

Extend the existing webhook infrastructure to handle attribute webhooks:

```mermaid
graph TD
    A[POST /workspaces/:id/fyle/exports/] --> B[ExportView.post]
    B --> C[async_import_and_export_expenses]
    C --> D{Check webhook action & resource}

    %% Existing flows
    D -->|EXPENSE/REPORT actions| E[Handle expense webhooks<br/>(existing logic)]

    %% New attribute flows
    D -->|CREATED + CATEGORY| F[Handle category creation]
    D -->|CREATED + PROJECT| G[Handle project creation]
    D -->|CREATED + COST_CENTER| H[Handle cost center creation]
    D -->|CREATED + Custom Field| I[Handle custom field creation]
    D -->|DELETE + Any attribute| J[Handle attribute deletion]

    F --> K[Check if webhook_sync_enabled in WorkspaceGeneralSettings]
    G --> K
    H --> K
    I --> K
    J --> L[Check if webhook_sync_enabled]

    K --> M{Webhook sync enabled?}
    L --> N{Webhook sync enabled?}

    M -->|Yes| O[async_task: sync_attribute_from_webhook]
    M -->|No| P[Skip - use traditional polling]
    N -->|Yes| Q[async_task: delete_attribute_from_webhook]
    N -->|No| P

    O --> R[End]
    Q --> R
    P --> R
    E --> R

    subgraph "New Webhook Body Examples"
        S["CREATE:
        {
          action: 'CREATED',
          resource: 'CATEGORY',
          data: {
            id: 123,
            org_id: 'orXX',
            name: 'Travel',
            is_enabled: true,
            ...
          }
        }"]

        T["DELETE:
        {
          action: 'DELETE',
          resource: 'CATEGORY',
          data: {
            org_id: 'orXX',
            id: 123
          }
        }"]
    end
```

### 2. New Webhook Processing Tasks

```mermaid
graph TD
    A[sync_attribute_from_webhook task] --> B[Extract webhook data]
    B --> C[Validate org_id matches workspace]
    C --> D[Determine attribute type mapping]

    D --> E{What type of sync needed?}
    E -->|New Fyle attribute| F[Sync directly to ExpenseAttribute table]
    E -->|Update existing attribute| G[Update existing ExpenseAttribute]
    E -->|Import to destination| H[Trigger reverse import if needed]

    F --> I[Create/Update ExpenseAttribute record]
    G --> I
    H --> J[Check if attribute needs to be imported to QBO]

    I --> K[Update mappings if applicable]
    J --> L{Import to QBO configured?}
    L -->|Yes| M[Trigger QBO import task]
    L -->|No| N[End]

    K --> O[Resolve any related errors]
    M --> N
    O --> N

    subgraph "Attribute Type Mapping"
        P[CATEGORY → ExpenseAttribute<br/>PROJECT → ExpenseAttribute<br/>COST_CENTER → ExpenseAttribute<br/>Custom Fields → ExpenseAttribute]
    end

    subgraph "Delete Flow"
        Q[delete_attribute_from_webhook] --> R[Mark ExpenseAttribute as inactive]
        R --> S[Update related mappings status]
        S --> T[Clean up QBO mappings if needed]
        T --> U[End]
    end
```

### 3. Enhanced WorkspaceGeneralSettings

Add webhook configuration to the settings model:

```mermaid
graph TD
    A[WorkspaceGeneralSettings Model] --> B[Existing Fields]
    A --> C[New Webhook Fields]

    B --> D[import_categories<br/>import_projects<br/>import_tax_codes<br/>import_vendors_as_merchants<br/>etc.]

    C --> E[webhook_sync_enabled: BooleanField<br/>webhook_sync_categories: BooleanField<br/>webhook_sync_projects: BooleanField<br/>webhook_sync_cost_centers: BooleanField<br/>webhook_sync_custom_fields: BooleanField]

    F[Import Settings API] --> G[User configures webhook settings]
    G --> H{Enable webhook sync?}
    H -->|Yes| I[webhook_sync_enabled = True]
    H -->|No| J[webhook_sync_enabled = False<br/>Use traditional polling]

    I --> K[Configure specific attribute types]
    K --> L[Save settings]
    J --> L
    L --> M[Triggers update scheduled tasks]

    subgraph "Migration Strategy"
        N[Phase 1: Add webhook fields with default=False]
        O[Phase 2: Gradual rollout per workspace]
        P[Phase 3: Default=True for new workspaces]
        Q[Phase 4: Deprecate polling (optional)]
    end
```

### 4. Hybrid Sync Architecture

Support both webhook and polling-based sync during transition:

```mermaid
graph TD
    A[Attribute Sync Request] --> B{webhook_sync_enabled?}

    B -->|True| C[Webhook-based Sync]
    B -->|False| D[Traditional Polling Sync]

    %% Webhook path
    C --> E[Receive webhook from Fyle]
    E --> F[Process webhook immediately]
    F --> G[Update local database]
    G --> H[Update sync timestamps]

    %% Polling path
    D --> I[Check sync intervals]
    I --> J{Time to sync?}
    J -->|Yes| K[Call Fyle API]
    J -->|No| L[Skip sync]
    K --> M[Batch process attributes]
    M --> N[Update local database]
    N --> O[Update sync timestamps]

    %% Convergence
    H --> P[Update mappings & resolve errors]
    O --> P
    L --> Q[End]
    P --> R[Trigger downstream processes]
    R --> Q

    subgraph "Benefits of Hybrid Approach"
        S[Real-time updates with webhooks<br/>Fallback to polling for reliability<br/>Gradual migration capability<br/>Reduced API calls<br/>Better user experience]
    end

    subgraph "Monitoring & Fallback"
        T[Track webhook delivery success<br/>Fall back to polling if webhooks fail<br/>Alert on webhook processing errors<br/>Health checks for both systems]
    end
```

## Implementation Plan

### Phase 1: Infrastructure Setup
1. Add webhook configuration fields to `WorkspaceGeneralSettings`
2. Create database migrations
3. Update import settings serializers and APIs
4. Add webhook processing tasks

### Phase 2: Webhook Handler Extension
1. Extend `async_import_and_export_expenses` to handle attribute webhooks
2. Implement attribute-specific processing logic
3. Add validation and error handling
4. Create monitoring and logging

### Phase 3: Testing & Rollout
1. Create comprehensive tests for webhook flows
2. Implement feature flags for gradual rollout
3. Add monitoring dashboards
4. Performance testing and optimization

### Phase 4: Migration Strategy
1. Enable webhooks for pilot workspaces
2. Monitor performance and reliability
3. Gradual rollout to all workspaces
4. Optional: Deprecate polling mechanism

## Key Benefits of Webhook Architecture

1. **Real-time Updates**: Immediate sync when attributes change in Fyle
2. **Reduced API Calls**: No need for periodic polling
3. **Better Performance**: Lower latency and resource usage
4. **Scalability**: Can handle high-frequency attribute changes
5. **User Experience**: Changes reflect immediately in the integration
6. **Cost Efficiency**: Fewer API calls reduce infrastructure costs

## Security Considerations

1. **Webhook Validation**: Verify webhook signatures from Fyle
2. **Rate Limiting**: Implement rate limits for webhook endpoints
3. **Idempotency**: Handle duplicate webhook deliveries gracefully
4. **Error Handling**: Robust error handling and retry mechanisms
5. **Monitoring**: Track webhook processing success/failure rates

## Migration Path

The hybrid architecture allows for a smooth transition:

1. **Current State**: Only polling-based sync
2. **Transition State**: Both webhook and polling available (controlled by settings)
3. **Future State**: Primarily webhook-based with polling as fallback
4. **End State**: Webhook-only (optional, based on reliability metrics)

This approach ensures zero downtime and provides flexibility to rollback if needed.
