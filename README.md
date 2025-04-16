# 🧾 Abusive Relationship Stories: Annotated Reddit Dataset

This repository contains a dataset of ~8000 Reddit posts related to potentially abusive romantic relationships. 
The posts were automatically annotated using a state-of-the-art Large Language Model (LLM), with guidance and partial review provided by domain experts in domestic abuse from the Michal Sela Forum.

To request access to the dataset, please fill out the following form:

👉 [Request Access Form](https://forms.gle/sU1tT9C6yEoGNVZ96)

Access is granted for academic and research purposes only. Approved applicants will receive a private download link.
---

## 🧠 Dataset Description

Each post in the dataset contains:

- **Post Metadata**: Extracted directly from Reddit.
- **Relationship & Demographic Metadata**: Automatically extracted using Google’s Gemini-pro LLM.
- **Contextual Risk Factors**: Annotated by the LLM based on known signs of abuse.

> ⚠️ LLM-based annotations may include errors and should be used as **guidance**, not ground truth.

---

## 📚 Source Subreddits

The dataset was curated from:
```
abusiverelationships, emotionalabuse, NarcissisticSpouses, NarcAbuseAndDivorce,
domesticviolence, abusesurvivors, relationship_advice, survivinginfidelity,
LifeAfterNarcissism, ToxicRelationships, relationships, Infidelity
```

---

## 🚫 Filtering Criteria

Posts were excluded if:
- The author was under 18.
- The post was not a personal story.
- The post was unrelated to romantic relationships.
- The post was too short or too long.

> ⚠️ Filtering was automated and may contain false positives.

---

## 🔍 Features

### 📝 Reddit Metadata

#### Post-level:
- `post_id`, `title`, `post_author`, `body`, `post_body`, `date_time`, `url`, `score`, `num_comments`, `flairs`, `subreddit`

#### Comment-level:
- Highest scored & longest comment info: `*_comment_id`, `*_comment_body`, `*_comment_author`, `*_comment_date_time`, `*_comment_score`

---

### 💞 Relationship Metadata (LLM)
Fields (sample answers in parentheses):
- `children` (yes/no/irrelevant/cannot be inferred)
- `relationship_type` (e.g., dating, married)
- `was_breakup`, `relationship_status`, `when_breakup`
- `living_with`

---

### 👥 Demographic Metadata (LLM)
- `author_role` (e.g., victim, offender, relative)
- `age_female`, `age_male`
- `author_gender`, `age_victim`, `age_offender`
- `gender_victim`, `gender_offender`

---

### ⚠️ Contextual Risk Factors (LLM)

Each risk is annotated with:
- **Yes** / **No** / **Plausibly** / **Cannot Be Inferred**

#### Risk Categories:
- **Violence**: `emotional_violence`, `physical_violence`, `sexual_violence`, `economic_violence`, `spiritual_violence`
- **Behavioral**: `gaslighting`, `obsessiveness`, `jealousy`, `outbursts`, `aggressive_behavior`
- **Background**: `past_offenses`, `ptsd`, `hard_childhood`, `mental_condition`, `unemployment`, `substance_use`
- **Control**: `daily_activity_control`, `fear_based_relationship`, `property_damage`, `access_to_weapons`
- **Relational**: `attempts_to_end_relationship`, `refusal_to_end_relationship`, `public_private_discrepancy`, `narcissistic_traits`
- **Support Systems**: `victim_support_network`, `offender_support_network`
- **Others**: `abusive_relationship`, `humiliation`, `signs_of_injury`, `presence_of_others_in_assault`, `suicidal_threats`, `emotional_dependency`

---

## 🧑‍⚕️ Expert Annotation

A small subset of <20 posts was reviewed by trained domestic abuse professionals for annotation calibration and validation of the LLM outputs.

---

## 📘 Appendix: Acronyms & Terms

| Acronym | Meaning |
|--------|---------|
| AP | Affair partner |
| BS/BP | Betrayed spouse/partner |
| DV | Domestic violence |
| DARVO | Deny, Attack, Reverse Victim and Offender |
| EA/PA | Emotional/Physical affair |
| NC | No contact |
| NEX | Narcissistic ex |
| PTSD | Post-traumatic stress disorder |
| RIC | Reconciliation Industrial Complex |
| Trickle-truth | Gradual, partial confession following evidence |
| Hoovering | Attempt by abuser to re-engage the victim |
| Monkey branching | Lining up a new relationship while still in the old one |

