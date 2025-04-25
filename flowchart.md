flowchart TD
    A([Start]) --> B["Define target URL\n'https://www.cgesp.org/...'"]
    B --> C["Send HTTP GET request\n(requests.get)"]
    C --> D["Parse HTML content\n(BeautifulSoup)"]
    D --> E["Find <style> tag and\nextract CSS text"]
    E --> F["Use regex to search for\n.condTempo class background image"]
    
    F --> G{Regex found\na match?}
    
    G -->|Yes| H["Extract image URL\n(match.group(1))"]
    H --> I["Combine base URL + image path\n(urljoin)"]
    I --> J["Return final image URL"]
    
    G -->|No| K["Return None"]
    
    J --> L["In __main__:\nPrint final URL"]
    K --> L
    L --> M([End])
    
    style A fill:#2ecc71,stroke:#27ae60
    style M fill:#e74c3c,stroke:#c0392b
    style B,C,D,E,F,H,I,J,K fill:#3498db,stroke:#2980b9
    style G fill:#f39c12,stroke:#e67e22
