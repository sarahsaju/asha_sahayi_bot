# Ethical AI Statement – ASHA Sahayi

## 1. Purpose and Scope

ASHA Sahayi is designed as a **decision-support assistant** for ASHA (Accredited Social Health Activist) frontline health workers in India.  
It is **not** a diagnostic system, treatment engine, or replacement for qualified healthcare professionals.

The system’s ethical goal is to **support safer field-level decision-making**, **encourage early referral**, and **reduce misinformation**, while respecting the operational realities of India’s public health system.

---

## 2. Alignment with Indian Public Health Context (ICMR-Style Design)

ASHA Sahayi follows **instructional, referral-oriented phrasing** aligned with the spirit of Indian public health advisories (ICMR / MoHFW style), which emphasize:

- Observation over diagnosis  
- Referral over treatment  
- Feasibility in low-resource settings  
- Clear responsibility boundaries  

The bot avoids speculative or definitive statements and instead uses **directive yet non-authoritative language** such as:
- “ശ്രദ്ധിക്കുക” (observe)
- “ഉണ്ടോയെന്ന് പരിശോധിക്കുക” (check for)
- “ഉടൻ PHC സമീപിക്കുക” (refer promptly)

This ensures the guidance is **actionable within the ASHA worker’s role** and does not conflict with formal medical authority.

---

## 3. Medical Safety and Non-Maleficence

To prevent medical harm, ASHA Sahayi enforces strict safety constraints:

- ❌ No medical diagnosis  
- ❌ No medicine names  
- ❌ No dosage information  
- ❌ No treatment decisions  

Instead, the bot provides:
- General observation points  
- Red-flag (danger sign) prompting  
- Clear referral advice  

This protects patients from unsafe guidance and **protects ASHA workers from legal, ethical, or professional risk**.

---

## 4. Medication Safety and Worker Protection

Medication-related queries are treated as **high-risk**.

If a user asks about:
- Tablets or syrups  
- Dosage (mg/ml)  
- Antibiotics or specific drugs  

The system:
- Firmly refuses to answer  
- Clearly explains its limitation  
- Directs the worker to a PHC or doctor  

This design explicitly **prevents task-shifting beyond ASHA scope** and safeguards ASHA workers from unintended liability.

---

## 5. Referral-Centred and Red-Flag–Driven Design

ASHA Sahayi is intentionally **referral-first**, not reassurance-first.

The system:
- Prompts ASHA workers to check for danger signs  
- Highlights symptoms requiring urgent attention  
- Encourages **early referral** even in uncertain cases  

Red-flag prompting improves:
- Early identification of serious conditions  
- Timely escalation to PHC  
- Safer outcomes at the community level  

This design reflects real ASHA workflows and supports public health triage rather than diagnosis.

---

## 6. Ask-Before-Advise to Reduce Hallucination

To avoid unsafe assumptions, the bot uses a **minimal ask-before-advise pattern**, requesting only essential clarifications such as:

- Age group  
- Duration of symptoms  
- Presence of danger signs  

This:
- Reduces AI hallucination  
- Improves contextual accuracy  
- Mirrors how ASHA workers collect information in the field  

The system never proceeds to guidance without basic context.

---

## 7. Language, Literacy, and Cognitive Load Considerations

ASHA Sahayi is designed for **real-world field conditions**, where:

- Literacy levels may vary  
- Cognitive load is high  
- Time is limited  

Therefore:
- Responses are in **simple Malayalam**  
- Medical jargon is avoided  
- Messages are **short, structured, and actionable**  
- Bullet points are used instead of long explanations  

This ensures usability during home visits and community interactions.

---

## 8. Data Privacy and Minimization

The system follows **privacy-by-design principles**:

- No Aadhaar numbers collected  
- No phone numbers or addresses stored  
- No personal identifiers required  
- Patients are logged using **local, non-identifying labels** only  

Visit data is stored locally using SQLite and is not shared externally.

---

## 9. Human-in-the-Loop Responsibility

All final decisions remain with:
- ASHA workers  
- Doctors  
- Public health institutions  

ASHA Sahayi does not act autonomously and does not override human judgment.

The AI functions strictly as a **support tool**, not a decision-maker.

---

## 10. Transparency and Limitations

The system explicitly communicates that:
- It is not a doctor  
- It does not provide treatment  
- It cannot replace medical consultation  

These limitations are communicated **directly to users** through disclaimers in responses.

---

## Conclusion

ASHA Sahayi demonstrates that generative AI can be used **ethically and responsibly** in community health settings when:

- Public health context is respected  
- Referral is prioritised  
- Safety overrides capability  
- Human judgment remains central  

The project prioritizes **patient safety, ASHA worker protection, and trust**, aligning with Indian public health ethics and field realities.
