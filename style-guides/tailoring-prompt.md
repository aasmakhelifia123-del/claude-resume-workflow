# Resume Tailoring Prompt

Copy-paste this at the start of a Claude conversation when you want to tailor your resume for a specific job. Attach three things along with this prompt:

1. The **master resume** (`resume.md`)
2. The **style guide** (`resume-style-guide.md`)
3. The **job description** (paste the text or attach the posting)

---

## The prompt

I'm tailoring my master resume for a specific role. I've attached three things:

1. **My master resume** (in project) — this is my kitchen-sink doc with everything I've done, not something I'd send as-is.
2. **My resume style guide** (in project) — captures my voice, framing rules, and editorial preferences. Follow it.
3. **The job description** — the role I'm tailoring for.

Before you draft anything, do this:

1. Read the JD and tell me the **2–3 requirements or signals** you think matter most for this role, and why. Include things that are stated explicitly (required skills, tools, years) and things implied by the company/team context (e.g., "security-forward startup → they care about someone who thinks architecturally about access").
    
2. Tell me which bullets from the master resume you'd **prioritize**, which you'd **cut**, and which you'd **tighten or rewrite** to match the JD's framing. Briefly explain the reasoning.
    
3. Flag anything you're **uncertain about** — honesty calibration questions, tool names to double-check, claims that feel borderline, places where the JD asks for something I haven't directly done.
    
4. Wait for my sign-off before producing the tailored draft.
    

Once I've signed off:

5. Produce the tailored resume. Follow the style guide — especially the calibration note that I tend to downplay, and to lean toward the strongest honest framing.
    
6. Keep it to one page if possible, or just over. Prefer cutting whole bullets to making individual bullets weaker.
    
7. After the draft, tell me:
    
    - What you kept, cut, and changed (brief summary)
    - Any bullets you're unsure about
    - Anything the JD asks for that the resume doesn't currently address well, so I can decide whether to add/reframe or leave it for the cover letter

---

## Notes to self

- If Claude starts drafting without doing steps 1–4, stop it and ask for the audit first. The audit is where the real thinking happens.
- The style guide is doing a lot of work — if something in the output feels off, check whether the guide needs updating vs. whether it's just a one-off miss.
- Tailored resumes are different from the master. Don't paste tailored edits back into the master unless they'd improve the master for future tailoring.