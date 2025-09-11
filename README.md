## ⚽ Soccer Analytics Pipeline: FA Women's Super League Data Processing & Analysis

## 📝 **Author**

**Designed by Michael Xu**  

## 📋 **Pipeline Overview**
This comprehensive notebook processes FA Women's Super League data from StatsBomb, transforming match-level events into player-level statistics and providing advanced analytics for recruitment and performance evaluation.

## 🎯 **Pipeline Components**

#### **1. Data Acquisition & Setup**
- **StatsBomb Integration**: Fetches FA Women's Super League match data (326 matches)
- **Dependencies**: pandas, numpy, matplotlib, seaborn, statsbombpy
- **Data Structure**: Event-level data → Player-level statistics

#### **2. Core Processing Engine**
- **PlayerLevelAnalyzer Class**: Main processing engine
- **Event Processing**: Location parsing, distance calculations, progressive pass detection
- **Statistical Aggregation**: 40+ player metrics including passes, shots, dribbles, tackles, xG

#### **3. Advanced Performance Scoring System (PSCDL Framework)**
- **5-Subscore System**:
  - **P (Passing/Creation)**: Playmaking, creativity, assists
  - **S (Finishing/Shot Value)**: Clinical finishing, goal scoring
  - **C (Carrying/1v1)**: Dribbling, ball carrying, 1v1 ability
  - **D (Defending/Disruption)**: Defensive actions, ball winning
  - **L (Discipline)**: Clean play, low foul rate
- **Weighted Performance Score**: `0.25P + 0.25S + 0.20C + 0.20D + 0.10L`

#### **4. Multi-Level Data Aggregation**
Creates 5 structured datasets for comprehensive analysis:
- **`statistics_totals.csv`**: Raw totals (goals, assists, minutes, etc.)
- **`statistics_per_game.csv`**: Per-game averages and rates
- **`statistics_per_minute.csv`**: Per-minute metrics
- **`statistics_per_90.csv`**: Standardized per-90 minute metrics
- **`statistics_performance_scores.csv`**: PSCDL scores and weighted performance

#### **5. Recruitment Analytics & Visualization**
- **Specialist Identification**: Top performers in each PSCDL area
- **Hidden Gems Detection**: High-potential players with lower overall scores
- **Interactive Comparison Tools**: Side-by-side player evaluation
- **Radar Area Metrics**: Overall ability coverage measurement

## 📊 **Output Datasets**

| Dataset | Players | Columns | Purpose |
|---------|---------|---------|---------|
| `statistics_totals.csv` | 395 | 30 | Raw totals and basic info |
| `statistics_per_game.csv` | 395 | 36 | Per-game averages and rates |
| `statistics_per_minute.csv` | 395 | 35 | Per-minute metrics |
| `statistics_per_90.csv` | 395 | 35 | Standardized per-90 metrics |
| `statistics_performance_scores.csv` | 395 | 9 | PSCDL scores and performance |

## 📈 **Key Insights**

Top scorers by total stats:
<img width="1989" height="790" alt="image" src="https://github.com/user-attachments/assets/cf517aea-3e7e-44ca-b249-00dc6022c374" />


Top scorers per 90 mins:
<img width="1991" height="790" alt="image" src="https://github.com/user-attachments/assets/4b3722b6-7fa5-4b54-beca-2fb29819b3c9" />

#### **Performance Distribution**
<img width="541" height="337" alt="image" src="https://github.com/user-attachments/assets/d12cd508-45ce-4fa9-8a7f-7f634256282d" />

- **Mean Performance Score**: 50.9 (normal distribution)
- **Top 10% Threshold**: 58.1
- **Elite Players**: <1% above 64.2

#### **Top Performers**

<img width="2598" height="1598" alt="Top Scorers" src="https://github.com/user-attachments/assets/71fdb7a6-d0ba-4987-8d64-33b9030b30ca" />

- **Overall Coverage**: Crystal Alyssia Dunn Soubrier (51.5 theoretical norm)
- **Finishing**: Vivianne Miedema, Nikita Parris, Samantha Kerr
- **Passing/Creation**: Alex Greenwood, Lucy Bronze, Leah Williamson
- **Defending**: Angharad James, Kayleigh Green

## 🎯 **Next Steps & Extensions**

#### **Potential Enhancements**
- **Clustering Analysis**: Player archetype identification
- **Predictive Modeling**: Performance prediction algorithms
- **Market Value Estimation**: Economic player valuation

#### **Limitations**
- **Position Analysis**: Player position can help develop more advance analysis
- **Potential Improvement on PSCDL Scoring Framework**: Can be more creative or specificed framework based on different needs (like different position)

---

*This pipeline provides a foundation for advanced soccer analytics, enabling evidence-based decision making in player recruitment, performance evaluation, and tactical planning.*





