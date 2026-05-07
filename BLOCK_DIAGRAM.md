# System Block Diagram

```mermaid
flowchart TD
    A[User Story Request] --> B[Bedtime State Detector]
    B --> C[Blueprint Planner]
    M[User Memory Card] --> C
    C --> D1[Story Candidate 1]
    C --> D2[Story Candidate 2]
    D1 --> Q[Quality Judge]
    D2 --> Q
    D1 --> S[Safety Judge]
    D2 --> S
    Q --> X[Candidate Selector]
    S --> X
    X -->|Fails threshold| R[Rewrite Agent]
    R --> Q
    R --> S
    X -->|Passes threshold| P[Final Rhythm Polish]
    P --> G[Final Story Output]
    Q --> H[Performance + Explainability]
    S --> H
    G --> U[Persist Story + Update Memory]
```

## Notes
- The model is fixed to `gpt-3.5-turbo` as required.
- Uses dual judges: quality and pediatric safety.
- Uses self-play candidate generation and selects highest combined quality+safety score.
- Memory card carries user continuity signals across nights.
