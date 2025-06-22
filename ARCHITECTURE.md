# System Architecture Diagram

This diagram provides a visual overview of the Data Agent Platform's architecture, illustrating the flow of information from the user to the backend services and back.

```mermaid
graph TD
    subgraph "User Interface (Dash/Plotly)"
        direction LR
        User([<fa:fa-user> User])
        WebApp{Data Agent Platform UI}

        User -- "1. Selects Dataset & Enters Natural Language Query" --> WebApp
    end

    subgraph "Backend System (Python & Google ADK)"
        direction TB
        Orchestrator(Orchestrator - Dash Callbacks)
        WebApp -- "2. Triggers Agent Workflow" --> Orchestrator

        subgraph "Coordinated Agents"
            direction LR
            SchemaAgent["<fa:fa-database> SchemaAgent"]
            DataAnalystAgent["<fa:fa-cogs> DataAnalystAgent"]
            VisualizationAgent["<fa:fa-chart-bar> VisualizationAgent"]
        end
    end

    subgraph "Google Cloud Services"
        direction TB
        BigQuery[("<fa:fa-google> Google BigQuery")]
        VertexAI[("<fa:fa-google> Vertex AI<br/>(Gemini LLM)")]
    end

    %% --- Data Flow ---
    Orchestrator -- "3. Get Schema" --> SchemaAgent
    SchemaAgent -- "4. Connects to" --> BigQuery
    BigQuery -- "5. Returns Schema" --> SchemaAgent
    SchemaAgent -- "6. Provides Schema to" --> DataAnalystAgent

    Orchestrator -- "7. Process Query" --> DataAnalystAgent
    DataAnalystAgent -- "8. Generates SQL via" --> VertexAI
    VertexAI -- "9. Returns SQL" --> DataAnalystAgent
    DataAnalystAgent -- "10. Executes SQL on" --> BigQuery
    BigQuery -- "11. Returns Data" --> DataAnalystAgent
    DataAnalystAgent -- "12. Forwards Data to" --> VisualizationAgent

    VisualizationAgent -- "13. Generates Chart & Insights" --> Orchestrator
    Orchestrator -- "14. Renders Output" --> WebApp

    %% --- Styling ---
    classDef user fill:#e3f2fd,stroke:#333,stroke-width:2px,color:#000
    classDef webapp fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    classDef orchestrator fill:#f8bbd0,stroke:#333,stroke-width:2px,color:#000
    classDef agent fill:#c8e6c9,stroke:#333,stroke-width:2px,color:#000
    classDef gcp fill:#d1c4e9,stroke:#333,stroke-width:2px,color:#000

    class User user;
    class WebApp webapp;
    class Orchestrator orchestrator;
    class SchemaAgent,DataAnalystAgent,VisualizationAgent agent;
    class BigQuery,VertexAI gcp;
```
