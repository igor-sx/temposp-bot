```mermaid
graph TD
    A[Start scrape_and_save] --> B{Call scrape_image_url(url)};

    subgraph scrape_image_url
        direction LR
        S1[Fetch HTML from url] --> S2[Parse HTML];
        S2 --> S3[Find style tag];
        S3 --> S4[Extract background URL via regex];
        S4 --> S5{URL Found?};
        S5 -- Yes --> S6[Construct final_url];
        S5 -- No --> S7[final_url = None];
        S6 --> S8[Return final_url];
        S7 --> S8;
    end

    B -- Returns final_url --> C{Is final_url valid (not None)?};
    B -- Exception during scrape --> X[Print Scrape Error];
    X --> E[Return False];
    C -- Yes --> D{Call download_image(final_url, image_path)};

     subgraph download_image
        direction LR
        D1[GET request final_url] --> D2{Check HTTP Status (raise_for_status)};
        D2 -- OK --> D3[Open save_path];
        D3 --> D4[Write response content to file];
        D4 --> D5[Return True];
        D2 -- Error --> D6[Print Download Error];
        D6 --> D7[Return False];
     end

    C -- No --> E;
    D -- Returns True --> F[Return True];
    D -- Returns False --> E;
    F --> Z[End];
    E --> Z;
```