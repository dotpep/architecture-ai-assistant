```mermaid
graph LR
    A[Customer] -->|has|> B[Order]
    B -->|contains|> C[Order Item]
    C -->|references|> D[Product]
    D -->|belongs to|> E[Category]
    E -->|has|> D
    A -->|places|> B
    B -->|is processed by|> F[Employee]
    F -->|manages|> A
    F -->|processes|> B
    subgraph Database Entities
        A
        B
        C
        D
        E
        F
    end
    subgraph Relationships
        A --> B
        B --> C
        C --> D
        D --> E
        E --> D
        A --> B
        B --> F
        F --> A
        F --> B
    end
```