# Monetization, Mobile Companion & Sponsor Telemetry Spec — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Document:** Mobile Companion Telemetry, AdMob Ad Unit Integration & Commercialization Model  
> **Version:** 1.0.0  

---

## 1. Executive Commercialization Overview

VERIACT employs a dual-pronged deployment model:
1. **Enterprise B2B Security Layer (Primary)**: Consumption-based SaaS ($0.001 per verified action) and on-premises private VPC deployments for enterprise customers.
2. **Community & Mobile Companion App (Developer Edition)**: A cross-platform mobile companion app (Android/iOS) for engineering leads and compliance managers to receive real-time push alerts and approve `ESCALATE` actions on-the-go. The developer/freemium edition incorporates Google AdMob units and sponsor telemetry banners to sustain infrastructure hosting.

---

## 2. Google AdMob Specification (Mobile Companion App)

### 2.1 Ad Units & Layout Integration

```
┌──────────────────────────────────────────────────────────┐
│  VERIACT Mobile Auditor (Android / iOS)                 │
├──────────────────────────────────────────────────────────┤
│  [Top Banner Ad Unit: 320x50]                           │
│  "Google Cloud for AI: Accelerate Enterprise Workloads" │
├──────────────────────────────────────────────────────────┤
│  ⚡ PENDING ESCALATIONS (3)                             │
│                                                          │
│  ⚠ Action: make_payment                                  │
│  Vendor: XYZ Logistics (₹18,500)                         │
│  Risk: 0.74 (HIGH)                                       │
│  [ APPROVE ]        [ REJECT ]                           │
├──────────────────────────────────────────────────────────┤
│  📊 Live System Health: PROTECTED                        │
│  Today's Blocked Violations: 23                          │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Ad Unit Configuration & Test IDs

| Ad Unit Name | Format | Placement | Refresh Rate | Google AdMob Test Unit ID |
|---|---|---|---|---|
| `veriact_auditor_banner_top` | Adaptive Banner | Bottom/Top of Mobile Review Stream | 30 seconds | `ca-app-pub-3940256099942544/6300978111` |
| `veriact_benchmark_interstitial` | Interstitial | Displayed upon completing full 250-scenario benchmark run | Once per session | `ca-app-pub-3940256099942544/1033173712` |
| `veriact_freemium_rewarded` | Rewarded Video | Unlocks 500 free Deep-Tier verification credits in sandbox | On-demand user tap | `ca-app-pub-3940256099942544/5224354917` |

### 2.3 User Privacy & Consent (UMP SDK)
- Implements Google's **User Messaging Platform (UMP)** SDK to gather GDPR/ePrivacy Directive consent before initializing ad requests.
- No sensitive transaction payloads, invoice amounts, or company tokens are shared with the AdMob SDK; ad tracking operates strictly in isolated sandboxed contexts with anonymized advertising IDs.

---

## 3. Sponsor Integration Matrix (Hackathon Partners)

| Sponsor Category | Platform Partner | Integration Architecture |
|---|---|---|
| **Cloud Compute & Inference** | Google Cloud / Vertex AI | Primary hosting for FastAPI verification gateway; Gemini 1.5 Flash (Fast tier) and Gemini 1.5 Pro (Deep tier). |
| **Agent Orchestration** | LangChain / LangGraph | Official ecosystem middleware; packaged as `veriact-langgraph-interceptor` on PyPI. |
| **Vector Database** | Chroma / Pinecone | High-throughput semantic retrieval for corporate compliance policies and procurement SOPs. |
| **Telemetry & Observability** | OpenTelemetry / Datadog | Real-time distributed tracing connecting agent thought nodes to VERIACT verification latency spans. |

---

## 4. Enterprise SaaS Unit Economics

```
Average Monthly Agent Operations per Enterprise Customer: 1,000,000 actions
- 65% Low Risk (Fast Tier): 650,000 actions @ $0.0001 compute cost = $65.00
- 25% Medium Risk (Strong Tier): 250,000 actions @ $0.0008 compute cost = $200.00
- 10% High Risk (Deep Tier): 100,000 actions @ $0.0035 compute cost = $350.00
Total Infrastructure Verification Cost: $615.00 / month

Enterprise B2B Pricing: $0.0020 per action = $2,000.00 / month
Gross Margin: ~69.25% ($1,385.00 net margin per enterprise customer)
```

By intelligently routing low-risk actions away from expensive heavyweight models, VERIACT achieves a **69%+ gross margin** while delivering sub-400ms blended latency to enterprise clients.
