# Analysis of the Evolution of Alliances and Polarization in the French National Assembly (14th-17th Legislatures)

This repository contains a quantitative framework to track the structural evolution of political alliances and polarization in France from 2012 to the present. The project utilizes network analysis and Natural Language Processing (NLP) to analyze legislative behavior during the 14th, 15th, 16th, and 17th legislatures.

## Key Project Files

* **[Social_graph_final_report.pdf](./Social_graph_final_report.pdf)**: The complete analysis report, including methodology, visualizations, and sociopolitical interpretation of the results.
* **[notebook.ipynb](./Final_Project_Social_Graph.ipynb)**: The Jupyter notebook containing the code for the graph construction, community detection, and textual analysis.

## Project Overview

France is currently facing a political crisis characterized by legislative gridlock and the disruption of the traditional left-right cleavage. This instability has been driven by the rise of the *En Marche* movement and political extremes. Although qualitative assessments exist, this study provides a quantitative approach to understanding the structural distancing between groups that explains the current absence of a majority.

The analysis covers the period from 2012 to 2025, observing long-term legislative trends through official roll-call votes and parliamentary speeches.

## Data

The dataset was constructed using open data from the French National Assembly via the official data website and API endpoints.
* **Scope:** 14th, 15th, 16th, and 17th legislatures.
* **Volume:** Analysis of thousands of roll-call votes and speech transcripts.
* **Processing:** Creating graphs where nodes represent deputies and edges represent the percentage of shared votes.

## Methodology

To empirically verify structural shifts in political organization, the project employs two main technical approaches:

### 1. Network Analysis
* **Graph Construction:** Edges are weighted based on the ratio of shared "For" votes between deputies.
* **Community Detection:** Application of the **Louvain method** to identify empirical alliances (communities) and compare them with official party affiliations.
* 
### 2. Textual Analysis (NLP)
* **Goal:** To understand the underlying rationale and thematic priorities of the detected communities.
* **Technique:** Implementation of an adapted **TF-IDF** (Term Frequency-Inverse Document Frequency) method to identify vocabulary specific to each community while filtering out individual idiosyncrasies.

## Authors

This project was conducted by students from the **Technical University of Denmark (DTU)** for the course *02805 Social Graphs and Interactions*.

* **Rémi Berthelot**
* **Antoine Bois-Berlioz**
* **Pierre Hollebèque**

---

## Data Strucure

Le dossier `data` est structuré comme suit :

```
data/
├── all_actors/
│   ├── acteur/
│   ├── deport/
│   └── organe/
├── cr/
├── processed/
└── vote/
    ├── 14/
    │   └── Scrutins_XIV.json
    ├── 15/
    │   ├── VTANR5K15V1.json
    │   └── ...
    ├── 16/
    │   ├── VTANR5K16V1.json
    │   └── ... 
    └── 17/
        ├── VTANR5K17V1.json
        └── ...
```

# Data Links

## Votes

* **14**: [https://data.assemblee-nationale.fr/archives-anterieures/archives-14e/scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-14e/scrutins)
* **15**: [https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins)
* **16**: [https://data.assemblee-nationale.fr/archives-16e/votes](https://data.assemblee-nationale.fr/archives-16e/votes)
* **17**: [https://data.assemblee-nationale.fr/travaux-parlementaires/votes](https://data.assemblee-nationale.fr/travaux-parlementaires/votes)



