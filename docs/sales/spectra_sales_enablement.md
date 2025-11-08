---
title: Spectra FX Audit Platform — Sales Enablement Kit
version: v400
prepared_on: "2025-11-08"
---

# 1. ICP & Buyer Persona Snapshot

- **Primary Buyers**: CFO, Group Treasurer, VP Procurement, Head of FX Risk.
- **Secondary Influencers**: Treasury Operations Lead, Head of Compliance, CTO (sécurité).
- **Trigger Events**: Hausse des frais FX, expansion multi-devises, audits internes, pression ESG/conformité.
- **Pain Statements**:
  - "Nos spreads FX explosent et on manque de visibilité."
  - "Impossible de prouver le ROI des négociations bancaires."
  - "Les données sont dispersées, on n'a ni benchmarks ni alertes temps réel."

# 2. Discovery Checklist (Call J+0)

1. Volume mensuel FX (en €) et paires principales ?
2. Setup actuel : banques, fintechs, plateformes internes ?
3. KPIs suivis aujourd'hui (spread moyen, coût total, temps de traitement) ?
4. Gouvernance & conformité : exigences pays/RSSI, stockage EU ?
5. Deadline business : audit, board meeting, reporting ESG ?
6. Ressources internes disponibles pour le POC (tech, data, juridique) ?

# 3. Email Sequences

## 3.1 Outreach Initial (Cold Email #1)

```
Objet : Identifier 0,1% d'économies sur vos flux FX en 48h ?

Bonjour {{Prénom}},

Spectra FX Audit analyse 30 jours de vos flux FX (CSV anonymisé) et quantifie immédiatement :
- l'écart entre vos spreads actuels et les benchmarks de marché,
- le potentiel d'économies annualisées,
- les leviers d'action (routing, renégociation, auto-batching).

La version Enterprise inclut un pilot fee de €250, remboursé si nous n'identifions pas au moins 0,05% d'économies.

Souhaitez-vous que je vous envoie le lien d'upload sécurisé pour un premier audit gratuit ?

Bien à vous,  
{{Signature}}
```

## 3.2 Follow-up (Cold Email #2 — J+3)

```
Objet : {{Prénom}}, vos équipes trésorerie ont-elles 30 minutes cette semaine ?

- Rapport exécutif livré en -48h
- Audit trail et DPA prêts pour conformité
- Benchmarks dynamiques (pas de spreads figés)

Si le timing est bon, je vous réserve un créneau avec notre analyste FX senior.
Sinon, je vous partage volontiers un rapport anonymisé d'un client mid-market.

Qu'en dites-vous ?
```

## 3.3 Bump Email (Cold Email #3 — J+7)

```
Objet : Dernier rappel — audit FX Spectra

Nous clôturons les sessions gratuites cette semaine.  
Le slot de demain 9h CET est encore libre.

Répondez "Audit" et je vous envoie le lien d'upload sécurisé + NDA (si besoin).
```

# 4. Pilot Fee Playbook

- **Positionnement**: "Nous engageons un analyste senior pendant 7 jours. Si nous n'identifions pas 0,05% d'économies, nous vous créditons les €250."
- **Upsell Hook**: Intégration API, monitoring continu, alertes Slack/Teams.
- **Proof Point**: "Sur les 20 derniers pilotes, l'économie moyenne constatée est de 0,12% du volume."

# 5. Pitch Deck Outline (10 Slides)

1. **Vision** — "Rationnaliser chaque pip dépensé en FX."
2. **Problème** — Opacité spreads, hétérogénéité data, manque de gouvernance.
3. **Solution** — Architecture Spectra v400 (multi-tenant, ML, observabilité).
4. **Traction** — KPI (N clients, POC won, temps audit → POC).
5. **Produit** — Demo workflow (Upload → Analyse → Executive Summary).
6. **Sécurité & Conformité** — DPA, ISO roadmap, audit trail immuable.
7. **Monétisation** — Plans Free/Standard/Enterprise + Pilot Fee.
8. **Roadmap** — v500 (optimisation FX temps réel, AI assistants).
9. **Equipe** — Fondateurs, advisor compliance & FX.
10. **Next Steps** — Upload data, call analyste, signature POC.

# 6. One-Pager (PDF / Email Layout)

- **Header**: Logo Spectra, baseline "FX Audit SaaS multi-tenant".
- **Section 1 — Pourquoi maintenant ?**  
  Hausse volatilité FX (+32% YoY), pression CFO pour preuves ROI, obligations audit ESG.
- **Section 2 — Ce que fait Spectra**  
  Normalise vos données FX, compare vs benchmarks dynamiques, recommande 3 actions chiffrées.
- **Section 3 — Résultats mesurés**  
  - 0,18% d'économies ≈ €1,8M sur €1 Md volume.  
  - Rapport exécutif 48h, anomalies alertées via webhook/Slack.  
  - Audit trail immuable, logs signés.
- **Section 4 — Packages**  
  Tableau récapitulatif Free / Standard / Enterprise + Pilot Fee.
- **Section 5 — Sécurité & Conformité**  
  DPA, hébergement EU, SOC 2 en cours, chiffrement TLS 1.2+, logs 365 jours.
- **CTA**  
  `Commencer l'audit gratuit` — bouton + QR code lien upload.

# 7. Objection Handling

| Objection | Réponse | Preuve |
|-----------|---------|--------|
| "On n'a pas le droit de partager les données." | Données anonymisées, DPA + SCC, destruction sous 7 jours. Offre d'audit sur sandbox avec données synthétiques. | Checklist conformité, clause consentement MSA, SOC 2. |
| "Nos banques nous donnent déjà de bons taux." | Spectra fournit un benchmark chiffré + recommandations (routing, netting). Objectif : prouver ce qui fonctionne et identifier micro-gains. | Cas client : 0,07% gain malgré banque Tier 1. |
| "Pas de bande passante interne." | Upload en 2 clics, mapping auto (CurrencyCloud, Stripe, Wise). Support onboarding en 30 minutes. | Script Python auto-mapping + support analyste dédié. |
| "Budgets gelés." | Free trial + pilot fee remboursable. ROI garanti ou crédité. | TCO < 1 FTE; savings > frais abonnement dans 84% cas. |

# 8. KPI de Vente & Pipeline

- **North Star**: Temps moyen entre partage data et signature POC.
- **Conversions clés**:
  - Call → Upload sécurisé (<2h cible).
  - Upload → Executive Summary (<48h).
  - Summary → Pilot Fee (<5 jours).
  - Pilot → Standard/Enterprise (<30 jours).
- **Dashboard**: Pipeline par industrie, % leads multi-pays, taux finalisation DPA.

# 9. Enablement Assets à produire (Roadmap)

- Script de démo (video Loom 6 min).
- Études de cas sectorielles (Retail, SaaS, Manufacturing).
- Playbook Partenaires (banques, plateformes FX).
- Template contrat tripartite (Spectra - Client - Broker).

# 10. Quick Reference Cheatsheet

- **Slogan**: "Spectra — l'analyse FX qui prouve son ROI en 48h."
- **3 chiffres clés**: 48h, 0,12%, €250 pilot fee.
- **Différenciateur**: Multi-tenant sécurisé + ML + audit trail cryptographique.
- **Call clôture**: "Si on ne trouve pas 0,05% d'économies, on vous rembourse le pilot fee. Vous voulez bloquer le slot 9h demain ?"
