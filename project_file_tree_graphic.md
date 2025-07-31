# תרשים גרפי של כל קבצי הפרויקט עם סימון נקודות כשל

```mermaid
graph TD
    A[.env]:::danger
    B[.gitignore]
    C[README.md]
    D[TO-DO.md]:::warn
    E[all_files_tree.txt]:::temp
    F[agents_system_full_report.xlsx]
    G[charles_github_api_openapi_fixed.yaml]
    H[charles_github_api_simple.yaml]
    I[run_dashboard.py]
    J[main_dashboard.py]
    K[improved_dashboard.py]
    L[multi_stock_dashboard.py]
    M[complete_system_dashboard.py]
    N[live_trading_dashboard.py]
    O[agent_management_dashboard.py]
    P[main_hub_dashboard.py]
    Q[simple_live_dashboard.py]
    R[comprehensive_live_dashboard.py]
    S[agent_monitoring_dashboard.py]
    T[test_dashboard.py]
    
    subgraph core
        core1[advanced_pattern_analyzer.py]
        core2[adx_score_agent.py]
        core3[ai_event_spotter.py]
        core4[__pycache__]:::cache
        core5[...]
    end
    
    subgraph utils
        utils1[credentials.py]:::danger
        utils2[data_fetcher.py]
        utils3[logger.py]
        utils4[__pycache__]:::cache
        utils5[...]
    end
    
    subgraph scripts
        scripts1[fill_yahoo_data.py]
        scripts2[test_advanced_analyzer.py]
        scripts3[__pycache__]:::cache
        scripts4[...]
    end
    
    subgraph data_files
        data1[INTC_10yr_history.csv]:::data
        data2[AAPL_history.csv]:::data
        data3[RGTI Stock Price History.csv]:::data
    end
    
    subgraph data
        data4[... (קבצי CSV/דאטה נוספים)]:::data
    end
    
    subgraph reports
        rep1[AGENT_UPGRADES_SUMMARY.md]
        rep2[DATA_SOURCES_STATUS.md]
        rep3[README.md]
        rep4[...]
    end
    
    subgraph temp_files
        temp1[.env.txt]:::temp
        temp2[all_binary_files.txt]:::temp
        temp3[all_project_files.txt]:::temp
        temp4[all_text_files.txt]:::temp
        temp5[env.example.txt]:::temp
        temp6[ingest_log.txt]:::temp
        temp7[requirements.txt]
        temp8[...]
    end
    
    subgraph vectorstore
        vec1[chroma.sqlite3]:::binary
        vec2[TO-DO.md]
        vec3[...]
    end
    
    subgraph __pycache__
        cache1[test_gap_detector_ultimate.cpython-313-pytest-8.4.1.pyc]:::cache
        cache2[test_openai_embedding.cpython-313-pytest-8.4.1.pyc]:::cache
        cache3[test_single_stock.cpython-313-pytest-8.4.1.pyc]:::cache
        cache4[...]
    end
    
    subgraph tests
        test1[test_gap_detector_ultimate.py]
        test2[test_openai_embedding.py]
        test3[test_single_stock.py]
        test4[...]
    end
    
    %% קישורים עיקריים
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
    R --> S
    S --> T
    T --> core
    T --> utils
    T --> scripts
    T --> data_files
    T --> data
    T --> reports
    T --> temp_files
    T --> vectorstore
    T --> __pycache__
    T --> tests

    classDef danger fill:#ffcccc,stroke:#ff0000,stroke-width:2px;
    classDef warn fill:#fff3cd,stroke:#ffcc00,stroke-width:2px;
    classDef temp fill:#e0e0e0,stroke:#888,stroke-width:1px;
    classDef cache fill:#f0f0f0,stroke:#888,stroke-width:1px;
    classDef data fill:#d1e7dd,stroke:#198754,stroke-width:1px;
    classDef binary fill:#d1c4e9,stroke:#512da8,stroke-width:1px;
```

---

**מקרא סימונים:**
- 🔴 danger: קובץ רגיש/סיכון אבטחה (סודות, מפתחות, הרשאות)
- 🟡 warn: קובץ שעלול להיות לא מעודכן/לא מנוהל
- ⚪ temp: קובץ זמני/פלט/לוג
- 🟢 data: קובץ דאטה/CSV
- 🟣 binary: קובץ בינארי/DB
- ⚫ cache: קובץ מטמון (__pycache__)

**כל קובץ מסומן לפי סוג הסיכון או התפקיד שלו.**

אם תרצה תרשים מפורט יותר (לכל קובץ במערכת), אפשר להרחיב!
