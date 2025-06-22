# System Architecture

## Visual Overview

```mermaid
graph TD
    %% Nodes
    User[User]:::user
    UI[Web Interface]:::ui
    Orchestrator[Orchestrator]:::orchestrator
    Schema[Schema Agent]:::agent
    Analyst[Data Analyst Agent]:::agent
    Visualizer[Visualization Agent]:::agent
    BQ[BigQuery]:::gcp
    AI[Vertex AI]:::gcp
    
    %% Connections
    User --> |1. Query| UI
    UI --> |2. Request| Orchestrator
    
    Orchestrator --> |3. Get Schema| Schema
    Schema --> |4. Query| BQ
    BQ --> |5. Return Schema| Schema
    Schema --> |6. Schema| Analyst
    
    Orchestrator --> |7. Process Query| Analyst
    Analyst --> |8. Generate SQL| AI
    AI --> |9. SQL| Analyst
    Analyst --> |10. Execute| BQ
    BQ --> |11. Results| Analyst
    Analyst --> |12. Data| Visualizer
    Visualizer --> |13. Visuals| Orchestrator
    Orchestrator --> |14. Display| UI
    
    %% Styling
    classDef user fill:#e3f2fd,stroke:#333,stroke-width:2px
    classDef ui fill:#fff9c4,stroke:#333,stroke-width:2px
    classDef orchestrator fill:#f8bbd0,stroke:#333,stroke-width:2px
    classDef agent fill:#c8e6c9,stroke:#333,stroke-width:2px
    classDef gcp fill:#d1c4e9,stroke:#333,stroke-width:2px
```

## Architecture Flow

### 1. User Interaction
- User accesses the web interface
- Selects a dataset and enters a natural language query

### 2. Request Handling
- Web interface sends the request to the Orchestrator

### 3. Schema Retrieval
- Orchestrator requests schema information from Schema Agent
- Schema Agent queries BigQuery for the dataset structure
- Schema is returned and passed to Data Analyst Agent

### 4. Query Processing
- Data Analyst Agent uses Vertex AI to convert natural language to SQL
- SQL is executed on BigQuery
- Query results are returned to the Data Analyst Agent

### 5. Visualization
- Results are sent to Visualization Agent
- Charts and insights are generated
- Final output is returned to the web interface

## Technical Components

### Frontend
- **Web Interface**: Built with Dash/Plotly for interactive visualizations

### Backend Services
- **Orchestrator**: Manages workflow between components
- **Schema Agent**: Handles dataset metadata and structure
- **Data Analyst Agent**: Processes natural language queries
- **Visualization Agent**: Generates charts and insights

### Cloud Services
- **Google BigQuery**: Data storage and query execution
- **Vertex AI**: Natural language processing and SQL generation

This architecture ensures a smooth flow from user query to data visualization while maintaining clear separation of concerns between components.
