"""
LLM prompt builder for generating Mermaid diagrams.
Constructs system prompts with diagram-type-specific Mermaid syntax rules.
"""

from typing import Dict


# Diagram-type-specific Mermaid syntax instructions
DIAGRAM_INSTRUCTIONS = {
    'flowchart': """
Generate a Mermaid flowchart diagram using the following syntax:

**Syntax Rules:**
- Start with `graph TD` (top-down) or `graph LR` (left-right)
- Define nodes: `A[Rectangle]`, `B(Rounded)`, `C{Diamond}`, `D((Circle))`
- Define connections: `A --> B` (arrow), `A --- B` (line), `A -.-> B` (dotted)
- Add labels to connections: `A -->|label| B`
- Subgraphs: `subgraph title ... end`

**Example:**
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[End]
    D --> E
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'erdiagram': """
Generate a Mermaid Entity-Relationship diagram using the following syntax:

**Syntax Rules:**
- Start with `erDiagram`
- Define entities and their relationships
- Relationship notation: `||--o{` (one-to-many), `||--||` (one-to-one), `}o--o{` (many-to-many)
- Add attributes: `ENTITY { type attribute }`
- Cardinality: `||` (exactly one), `|o` (zero or one), `}o` (zero or more), `}|` (one or more)

**Example:**
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string email
        int customerId
    }
    ORDER {
        int orderId
        date orderDate
    }
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'sequence': """
Generate a Mermaid sequence diagram using the following syntax:

**Syntax Rules:**
- Start with `sequenceDiagram`
- Declare participants: `participant A as Alice`
- Messages: `A->>B: Message` (solid arrow), `A-->>B: Response` (dotted arrow)
- Activation: `activate A` and `deactivate A`
- Notes: `Note right of A: Note text` or `Note over A,B: Note text`
- Loops: `loop description ... end`
- Alt/Else: `alt description ... else ... end`

**Example:**
```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant D as Database
    
    U->>S: Request data
    activate S
    S->>D: Query
    activate D
    D-->>S: Results
    deactivate D
    S-->>U: Response
    deactivate S
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'class': """
Generate a Mermaid class diagram using the following syntax:

**Syntax Rules:**
- Start with `classDiagram`
- Define classes: `class ClassName`
- Add attributes and methods inside class definition
- Relationships: `<|--` (inheritance), `*--` (composition), `o--` (aggregation), `-->` (association)
- Visibility: `+` (public), `-` (private), `#` (protected)
- Abstract: `<<interface>>` or `<<abstract>>`

**Example:**
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog
    
    class Owner {
        +String name
    }
    Owner --> Dog : owns
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'state': """
Generate a Mermaid state diagram using the following syntax:

**Syntax Rules:**
- Start with `stateDiagram-v2`
- Define states: `state "State Name" as s1`
- Transitions: `s1 --> s2 : event`
- Start state: `[*] --> s1`
- End state: `s1 --> [*]`
- Composite states: `state s1 { ... }`
- Choice: `state choice <<choice>>`
- Fork/Join: `state fork <<fork>>` or `state join <<join>>`

**Example:**
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Success : complete
    Processing --> Failed : error
    Success --> [*]
    Failed --> Idle : retry
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'architecture': """
Generate a Mermaid flowchart diagram for high-level system architecture using the following syntax:

**Syntax Rules:**
- Start with `graph TD` (top-down) or `graph LR` (left-right)
- Use subgraphs to represent system layers or components
- Define nodes for services, databases, external systems
- Use descriptive labels and clear connections
- Show data flow with labeled arrows

**Example:**
```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[Web UI]
        Mobile[Mobile App]
    end
    
    subgraph "Backend Layer"
        API[API Gateway]
        Auth[Auth Service]
        BL[Business Logic]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Cache)]
    end
    
    UI --> API
    Mobile --> API
    API --> Auth
    API --> BL
    BL --> DB
    BL --> Cache
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
""",
    
    'dfd': """
Generate a Mermaid flowchart diagram for Data Flow Diagram (DFD) using the following syntax:

**Syntax Rules:**
- Start with `graph TD` or `graph LR`
- External entities: Use rectangles `A[Entity]`
- Processes: Use rounded rectangles `B(Process)`
- Data stores: Use special notation `C[(Data Store)]`
- Data flows: Use labeled arrows `A -->|data| B`
- Number processes: `P1(Process 1)`, `P2(Process 2)`

**Example:**
```mermaid
graph LR
    User[User] -->|login request| P1(Authenticate)
    P1 -->|credentials| DB[(User Database)]
    DB -->|user data| P1
    P1 -->|auth token| User
    User -->|data request| P2(Process Request)
    P2 -->|query| DB2[(Application Database)]
    DB2 -->|results| P2
    P2 -->|response| User
```

Generate ONLY valid Mermaid code wrapped in ```mermaid code blocks.
"""
}


def build_system_prompt(diagram_type: str) -> str:
    """
    Build a system prompt with diagram-type-specific Mermaid syntax instructions.
    
    Args:
        diagram_type: The type of diagram to generate (flowchart, erdiagram, sequence, etc.)
        
    Returns:
        str: Complete system prompt with syntax instructions
        
    Raises:
        ValueError: If diagram_type is not supported
    """
    diagram_type_lower = diagram_type.lower()
    
    if diagram_type_lower not in DIAGRAM_INSTRUCTIONS:
        raise ValueError(f"Unsupported diagram type: {diagram_type}. "
                        f"Supported types: {', '.join(DIAGRAM_INSTRUCTIONS.keys())}")
    
    base_prompt = """You are an expert software architect and Mermaid diagram generator.
Your task is to create clear, accurate, and well-structured Mermaid diagrams based on user descriptions.

**Important Guidelines:**
1. Generate ONLY valid Mermaid syntax
2. Wrap your diagram code in ```mermaid code blocks
3. Keep diagrams clear and readable
4. Use appropriate node types and relationships
5. Add descriptive labels where helpful
6. Follow the syntax rules exactly as specified

"""
    
    diagram_instructions = DIAGRAM_INSTRUCTIONS[diagram_type_lower]
    
    return base_prompt + diagram_instructions


def build_user_prompt(user_description: str, diagram_type: str) -> str:
    """
    Build the user prompt that includes the diagram description and type.
    
    Args:
        user_description: User's natural language description of the diagram
        diagram_type: The type of diagram to generate
        
    Returns:
        str: Formatted user prompt
    """
    return f"""Create a {diagram_type} diagram for the following:

{user_description}

Remember to wrap your Mermaid code in ```mermaid code blocks."""


def build_complete_prompt(user_description: str, diagram_type: str) -> Dict[str, str]:
    """
    Build complete prompt with system and user messages.
    
    Args:
        user_description: User's natural language description of the diagram
        diagram_type: The type of diagram to generate
        
    Returns:
        Dict containing 'system' and 'user' prompt strings
        
    Raises:
        ValueError: If diagram_type is not supported
    """
    return {
        'system': build_system_prompt(diagram_type),
        'user': build_user_prompt(user_description, diagram_type)
    }


def get_supported_diagram_types() -> list:
    """
    Get list of supported diagram types.
    
    Returns:
        list: List of supported diagram type strings
    """
    return list(DIAGRAM_INSTRUCTIONS.keys())
