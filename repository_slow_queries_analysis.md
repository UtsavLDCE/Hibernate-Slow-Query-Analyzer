# Slow Queries Analysis Report
**File:** `/home/utsav-kakadiya/Downloads/05aug2025LogsDDPPOC/logs/repository.log`  
**Analysis Date:** August 6, 2025  
**Total Slow Queries Found:** 52

## Executive Summary

The analysis reveals that the system is experiencing performance issues primarily with:
1. **SoftwareComponent** queries (9 hits, 4720ms total)
2. **AssetChangeLog** operations (INSERT heavy - 5927ms total for ComponentData, 5907ms for main table)
3. **SsoConfig** lookups (5 hits, 3560ms total)

## Top Queries by Frequency (Most Hits)

### 1. SELECT SoftwareComponent
- **Hits:** 9
- **Total Time:** 4,720ms
- **Average Time:** 524ms
- **Max Time:** 1,158ms
- **Min Time:** 141ms

**Sample Query:**
```sql
select softwareco0_.id as id1_862_, softwareco0_.updatedById as updatedb2_862_, 
softwareco0_.updatedTime as updatedt3_862_, softwareco0_.createdById as createdb4_862_, 
softwareco0_.createdTime as createdt5_862_, ... from SoftwareComponent softwareco0_ 
where softwareco0_.refId=2938 order by softwareco0_.id asc
```

### 2. INSERT AssetChangeLogComponentData
- **Hits:** 6
- **Total Time:** 5,927ms
- **Average Time:** 988ms
- **Max Time:** 1,025ms
- **Min Time:** 923ms

**Sample Query:**
```sql
insert into AssetChangeLogComponentData (updatedById, updatedTime, createdById, 
createdTime, name, oobType, removed, removedById, removedTime, componentJson) 
values (2, 1754369299800, 2, 1754369299800, NULL, NULL, 'FALSE', 0, 0, '{...}')
```

### 3. INSERT AssetChangeLog
- **Hits:** 5
- **Total Time:** 5,907ms
- **Average Time:** 1,181ms
- **Max Time:** 2,648ms
- **Min Time:** 130ms

### 4. SELECT SsoConfig
- **Hits:** 5
- **Total Time:** 3,560ms
- **Average Time:** 712ms
- **Max Time:** 1,062ms
- **Min Time:** 480ms

**Sample Query:**
```sql
select ssoconfig0_.id as id1_882_, ssoconfig0_.updatedById as updatedb2_882_, 
... from SsoConfig ssoconfig0_ order by ssoconfig0_.id asc
```

### 5. SELECT FlotoUser
- **Hits:** 4
- **Total Time:** 1,910ms
- **Average Time:** 478ms
- **Max Time:** 589ms
- **Min Time:** 431ms

## Top 10 Slowest Individual Queries

| Rank | Operation | Table | Time (ms) | Timestamp |
|------|-----------|-------|-----------|-----------|
| 1 | INSERT | AssetChangeLog | 2,648 | 2025-08-05 06:47:33.670 |
| 2 | SELECT | SoftwareComponent | 1,158 | 2025-08-05 07:35:13.305 |
| 3 | SELECT | AgentBuildUpload | 1,131 | 2025-08-05 03:16:09.269 |
| 4 | INSERT | AssetChangeLog | 1,116 | 2025-08-05 06:47:55.864 |
| 5 | SELECT | SsoConfig | 1,062 | 2025-08-05 06:56:17.461 |
| 6 | SELECT | Workflow_WorkflowProcessBlock | 1,051 | 2025-08-05 03:50:20.457 |
| 7 | INSERT | AssetChangeLogComponentData | 1,025 | 2025-08-05 07:20:35.308 |
| 8 | INSERT | AssetChangeLog | 1,019 | 2025-08-05 07:20:35.310 |
| 9 | INSERT | AssetChangeLogComponentData | 1,010 | 2025-08-05 04:48:47.011 |
| 10 | SELECT | SsoConfig | 1,009 | 2025-08-05 06:56:17.403 |

## Complete Rankings by Query Type

| Query Type | Count | Total Time (ms) | Avg Time (ms) | Max Time (ms) | Min Time (ms) |
|------------|-------|-----------------|---------------|---------------|---------------|
| SELECT SoftwareComponent | 9 | 4,720 | 524 | 1,158 | 141 |
| INSERT AssetChangeLogComponentData | 6 | 5,927 | 988 | 1,025 | 923 |
| INSERT AssetChangeLog | 5 | 5,907 | 1,181 | 2,648 | 130 |
| SELECT SsoConfig | 5 | 3,560 | 712 | 1,062 | 480 |
| SELECT FlotoUser | 4 | 1,910 | 478 | 589 | 431 |
| INSERT HardwareAssetAudit | 3 | 1,574 | 525 | 619 | 452 |
| SELECT Manufacturer | 3 | 364 | 121 | 150 | 101 |
| SELECT Workflow_WorkflowProcessBlock | 2 | 1,405 | 702 | 1,051 | 354 |
| INSERT AssetScanAudit | 2 | 1,337 | 668 | 715 | 622 |
| SELECT HardwareAsset | 2 | 1,167 | 584 | 591 | 576 |
| SELECT Operand | 2 | 209 | 104 | 107 | 102 |

## Performance Recommendations

### Critical Issues (> 1000ms)
1. **AssetChangeLog INSERTs** - Extremely slow, up to 2.6 seconds
2. **SoftwareComponent SELECTs** - Consistently slow with many hits
3. **SsoConfig SELECTs** - Multiple slow lookups, likely missing indexes

### Optimization Suggestions

1. **Index Analysis Needed:**
   - `SoftwareComponent.refId` - Most queried field
   - `SsoConfig` - Full table scans apparent
   - `Manufacturer.displayName` - Case-insensitive lookups

2. **Query Optimization:**
   - Review complex joins in `Workflow_WorkflowProcessBlock` queries
   - Consider pagination for large result sets
   - Analyze `AssetChangeLog` insert performance - possible bulk operations

3. **Architecture Review:**
   - Consider caching for frequently accessed `SsoConfig` data
   - Review `AssetChangeLog` insert patterns - possibly batch operations

## Time Distribution Analysis

**Peak Performance Issues:**
- Morning hours (03:16 - 07:35) show consistent slow queries
- Asset discovery operations are particularly slow
- Change logging operations need immediate attention

**Most Problematic Operations:**
1. Asset change logging (both ComponentData and main table)
2. Software component lookups
3. SSO configuration retrievals
4. Complex workflow queries

This analysis indicates a need for immediate database performance tuning, particularly around indexing strategies and query optimization for the most frequently accessed tables.
