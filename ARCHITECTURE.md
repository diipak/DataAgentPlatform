# System Architecture Diagram

This diagram provides a visual overview of the Data Agent Platform's architecture, illustrating the flow of information from the user to the backend services and back.

```mermaid
graph TD
    %% User Interface
    User([User])
    WebApp[Data Agent Platform UI]
    
    %% Backend Components
    Orchestrator[Orchestrator]
    SchemaAgent[SchemaAgent]
    DataAnalystAgent[DataAnalystAgent]
    VisualizationAgent[VisualizationAgent]
    
    %% Cloud Services
    BigQuery[Google BigQuery]
    VertexAI[Vertex AI / Gemini LLM]

    %% User Flow
    User -->|1. Selects Dataset & Query| WebApp
    WebApp -->|2. Triggers Workflow| Orchestrator
    
    %% Schema Flow
    Orchestrator -->|3. Get Schema| SchemaAgent
    SchemaAgent -->|4. Connect| BigQuery
    BigQuery -->|5. Schema| SchemaAgent
    SchemaAgent -->|6. Schema| DataAnalystAgent
    
    %% Query Processing
    Orchestrator -->|7. Process Query| DataAnalystAgent
    DataAnalystAgent -->|8. Generate SQL| VertexAI
    VertexAI -->|9. SQL| DataAnalystAgent
    DataAnalystAgent -->|10. Execute| BigQuery
    BigQuery -->|11. Data| DataAnalystAgent
    DataAnalystAgent -->|12. Forward Data| VisualizationAgent
    
    %% Visualization
    VisualizationAgent -->|13. Charts & Insights| Orchestrator
    Orchestrator -->|14. Render| WebApp
    
    %% Styling
    classDef user fill:#e3f2fd,stroke:#333,stroke-width:2px
    classDef webapp fill:#fff9c4,stroke:#333,stroke-width:2px
    classDef orchestrator fill:#f8bbd0,stroke:#333,stroke-width:2px
    classDef agent fill:#c8e6c9,stroke:#333,stroke-width:2px
    classDef gcp fill:#d1c4e9,stroke:#333,stroke-width:2px
    
    class User user
    class WebApp webapp
    class Orchestrator orchestrator
    class SchemaAgent,DataAnalystAgent,VisualizationAgent agent
    class BigQuery,VertexAI gcp
```

## Architecture Flow Description

1. **User Interaction**: The user selects a dataset and enters a natural language query through the web interface.

2. **Orchestration**: The Dash web app triggers the workflow in the Orchestrator.

3. **Schema Retrieval**: 
   - The Orchestrator requests schema information from the SchemaAgent.
   - SchemaAgent connects to Google BigQuery to fetch the dataset schema.
   - The schema is provided to the DataAnalystAgent for context.

4. **Query Processing**:
   - The DataAnalystAgent uses Vertex AI (Gemini LLM) to convert the natural language query into SQL.
   - The generated SQL is executed on Google BigQuery.
   - Query results are returned to the DataAnalystAgent.

5. **Visualization**:
   - The DataAnalystAgent forwards the structured data to the VisualizationAgent.
   - VisualizationAgent generates charts and insights from the data.
   - Results are sent back through the Orchestrator to be displayed in the web interface.

6. **Display**: The final output (tables, charts, and insights) is rendered in the user's browser.
