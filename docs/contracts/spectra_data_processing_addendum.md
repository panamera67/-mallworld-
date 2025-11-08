---
title: Spectra FX Audit Platform — Data Processing Addendum (DPA)
version: v400
effective_date: "[Effective Date]"
parties:
  - Spectra Analytics SAS ("Processor" or "Spectra")
  - "[Client Legal Name]" ("Controller" or "Client")
---

This Data Processing Addendum ("DPA") forms part of the Master Service Agreement ("Agreement") between Spectra and Client. It governs the processing of Client Personal Data in connection with the Services and reflects the Parties' obligations under applicable Data Protection Laws, including Regulation (EU) 2016/679 (GDPR) and relevant national laws.

# 1. Definitions

Terms defined in the Agreement have the same meaning in this DPA. Additional definitions:

- **Data Protection Laws**: All laws and regulations applicable to the processing of Personal Data under the Agreement, including GDPR and, where applicable, the UK GDPR and Swiss FADP.
- **Personal Data**: Any information relating to an identified or identifiable natural person processed by Spectra on behalf of Client.
- **Processing**: Any operation performed on Personal Data, including collection, storage, use, disclosure, or deletion.
- **Sub-processor**: A third party engaged by Spectra to process Personal Data on behalf of Client.
- **Standard Contractual Clauses (SCCs)**: The European Commission's Standard Contractual Clauses for the transfer of Personal Data to third countries outside the EEA, as updated from time to time.

# 2. Roles and Responsibilities

2.1 **Controller/Processor Roles**. Client acts as Controller. Spectra acts as Processor when processing Client Personal Data.

2.2 **Documented Instructions**. Spectra will process Personal Data only on documented instructions from Client, including with respect to transfers of Personal Data to a third country, unless required to do so by law. Spectra will notify Client if an instruction infringes Data Protection Laws.

2.3 **Confidentiality**. Spectra ensures that its personnel authorized to process Personal Data are bound by confidentiality obligations and receive privacy and security training appropriate to their role.

# 3. Subject Matter and Duration

3.1 **Subject Matter**. The processing involves ingestion, analysis, and reporting on FX transaction data provided by Client, which may contain Personal Data associated with Client staff or counterparties.

3.2 **Duration**. Processing will extend for the Subscription Term under the Agreement and any additional retention period agreed in writing.

# 4. Nature and Purpose of Processing

Spectra processes Personal Data to:
- Provide analytics, benchmarking, optimization, and reporting services as defined in the Agreement,
- Maintain, secure, and improve the Platform,
- Provide support and incident response,
- Comply with legal obligations and audit requirements.

# 5. Categories of Data and Data Subjects

- **Categories of Personal Data** (as provided by Client): hashed identifiers, user access logs, trader identifiers (pseudonymized), contact information of Client personnel (for account management), and metadata contained in uploads.
- **Special Categories**: Client will avoid uploading special categories of data. If special categories must be processed, Parties will agree on additional safeguards.
- **Data Subjects**: Client employees, contractors, and authorized counterparts involved in FX transactions.

# 6. Security Measures

Spectra implements the technical and organizational measures described in Annex I (Security Measures), which include:
- Encryption in transit (TLS 1.2+) and at rest,
- Multi-tenant isolation with role-based access controls,
- Logging and monitoring with audit trails,
- Regular penetration testing and vulnerability management,
- Business continuity and disaster recovery plans with defined RTO/RPO targets.

# 7. Sub-processors

7.1 **Authorized Sub-processors**. Spectra may use the sub-processors listed in Annex II. Spectra will inform Client of any intended changes and provide an opportunity to object on reasonable grounds.

7.2 **Sub-processor Obligations**. Spectra ensures sub-processors are bound by written contracts imposing data protection obligations equivalent to this DPA. Spectra remains liable for sub-processor performance.

# 8. Data Subject Rights

Spectra will promptly notify Client of any requests received from Data Subjects relating to Personal Data. Spectra will assist Client, at Client's expense where permitted by law, in fulfilling Data Subject rights (access, rectification, deletion, restriction, portability, objection).

# 9. Personal Data Breach Notification

Spectra will notify Client without undue delay upon becoming aware of a Personal Data Breach. Notifications will describe the nature of the breach, likely consequences, measures taken, and contact point for further information. Spectra will cooperate with Client to meet regulatory obligations.

# 10. Data Protection Impact Assessments

Spectra will provide reasonable assistance to Client, at Client's expense where permitted, with Data Protection Impact Assessments and consultations with supervisory authorities relating to the Services.

# 11. Return and Deletion of Data

Upon termination or expiration of the Agreement, Spectra will, at Client's option and subject to legal retention requirements:
- Return Personal Data in a commonly used format, or
- Delete Personal Data within 30 days, ensuring non-recoverability.

Spectra may retain minimal Personal Data required to comply with legal obligations (e.g., accounting records) and will continue to protect such data per this DPA.

# 12. International Transfers

12.1 **Location of Processing**. Spectra processes Personal Data within the EEA and other countries listed in Annex II.

12.2 **Transfer Safeguards**. For transfers outside the EEA, Spectra will rely on an adequate transfer mechanism such as:
- SCCs incorporated by reference in Annex III,
- Binding Corporate Rules (if adopted by Spectra),
- Adequacy decisions, or
- Other mechanisms compliant with Data Protection Laws.

12.3 **Supplementary Measures**. Spectra implements supplementary safeguards (encryption, access controls, transparency reports) to ensure equivalence of protection for cross-border transfers.

# 13. Audits and Assessments

13.1 **Documentation**. Spectra will make available documentation and third-party audit reports (e.g., SOC 2 Type II, ISO 27001) necessary to demonstrate compliance.

13.2 **On-site Audits**. Client may perform on-site audits no more than once per 12-month period with 30 days' notice, except in emergencies or where required by law. Audits must minimize business disruption and are subject to confidentiality. Client bears all associated costs.

# 14. Liability

Liability under this DPA is subject to the limitations and exclusions set forth in the Agreement, except to the extent prohibited by Data Protection Laws.

# 15. Governing Law

This DPA is governed by the same law and jurisdiction as the Agreement, unless Data Protection Laws require otherwise.

# Annex I — Technical and Organizational Measures

1. **Governance**
   - Data protection officer appointment (if required) and privacy committee oversight.
   - Security policies reviewed annually and approved by executive leadership.

2. **Access Management**
   - Role-based access control, least privilege, and MFA for administrative access.
   - Automated provisioning/de-provisioning integrated with tenant management.

3. **Data Security**
   - Encryption at rest using AES-256.
   - Key management via secure key vault with rotation policies.

4. **Network Security**
   - Segmented VPC architecture with firewalls and network policies.
   - Continuous monitoring, IDS/IPS, and DDoS mitigation.

5. **Application Security**
   - Secure SDLC, code reviews, SAST/DAST scanners.
   - Dependency management with vulnerability alerts.

6. **Operations**
   - Regular backups stored in encrypted, geo-redundant locations.
   - Tested disaster recovery with RTO ≤ 4 hours and RPO ≤ 1 hour for enterprise tenants.

7. **Logging and Monitoring**
   - Centralized logging with tamper-evident storage.
   - Security event correlation and alerting with 24/7 escalation for enterprise plans.

# Annex II — Authorized Sub-processors (Sample)

| Sub-processor | Purpose | Location | Safeguards |
|---------------|---------|----------|------------|
| AWS (Ireland) | Infrastructure hosting | EU (Ireland) | ISO 27001, SOC 1/2 | 
| Stripe, Inc.  | Billing and payments | EU/US | SCCs, ISO 27001 |
| SendGrid      | Transactional email | US | SCCs, ISO 27001 |
| Datadog       | Monitoring | EU/US | SCCs, ISO 27001 |

Spectra will maintain an up-to-date list of Sub-processors at `https://spectrafx.com/subprocessors`.

# Annex III — Standard Contractual Clauses

The Parties agree that the SCCs (Module Two: Controller to Processor) are incorporated by reference, with Spectra as the data importer and Client as the data exporter. Annex I and Annex II of the SCCs are satisfied by the information provided in this DPA. Where the UK GDPR or Swiss law applies, the UK Addendum and Swiss Addendum (as applicable) are incorporated by reference.

# Signatures

Authorized representatives of the Parties have executed this DPA as of the Effective Date.

| Spectra Analytics SAS | [Client Legal Name] |
|-----------------------|---------------------|
| Name:                 | Name:               |
| Title:                | Title:              |
| Date:                 | Date:               |
| Signature:            | Signature:          |
