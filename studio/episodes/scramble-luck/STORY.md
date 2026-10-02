# How lucky is a lucky scramble? — story and scenes

Status: script draft v0 by Qwen 3.8 (local), 2026-10-02, for Sol 6.1 to revise; not locked; the title is a working title the owner decides.

## Argument: "The shared scramble/slot component"

| Beat | What the viewer learns | Claims |
|---|---|---|
| 1. Belief | Record solves are often called "lucky scrambles." | — |
| 2. Scope | We are not judging one record; we are measuring the shared component across all finalists. | SL-C002, SL-C003 |
| 3. Obvious answer | Look at a record reconstruction; it often looks easy. | SL-C137, SL-C138 |
| 4. Flaw | Luck that suits one solver is not luck everyone shares. | — |
| 5. Fairer test | Every finalist solves the same five scrambles; peer times reveal scramble difficulty. | SL-C005, SL-C007 |
| 6. Verdict | The shared component is small (~2%); data rule out a 10% boost. | SL-C001 |
| 7. Limitations | Slot conditions, DNFs, and personal luck cannot be fully separated. | SL-C075, SL-C076 |

Wording rules (METHOD.md): The video answers a narrower question than "was the record lucky?": how much the scramble difficulty shared by all finalists speeds up season-best final solves. The shared scramble/slot component is small, around 2% for these season bests, and the data rule out a shared boost as large as 10%. NEVER say "only 2% of the record was luck", never say the rest is personal luck, never make claims about one specific record's total luck, never call it pure scramble difficulty (it is the shared scramble/slot component). Explain scramble, cross, CFOP, PLL skip, and average of five in one sentence each. First person, curious and precise, light humour allowed.

## Scene table

| Scene | Viewer question | Claims | Visual (the design system decides the look) | Why next? |
|---|---|---|---|---|
| S01 The Belief | Are record solves just lucky scrambles? | — | Headlines quoting "lucky scramble"; a cube spinning | We need to define the scope. |
| S02 The Scope | What are we actually measuring? | SL-C002, SL-C003 | Map of competitions; counter of finals and solvers | We need the basics. |
| S03 The Basics | What is a scramble, cross, CFOP, etc.? | SL-C130, SL-C132 | Animated cube steps; text definitions | We need the obvious answer. |
| S04 The Obvious Answer | Does a record reconstruction look easy? | SL-C137, SL-C138 | Token counts for Du and Park; "easy" label | But is it shared luck? |
| S05 The Flaw | Is one solver's luck everyone's luck? | — | Two solvers, same scramble, different times; "Not shared" stamp | We need a fairer test. |
| S06 The Fairer Test | How do we measure shared difficulty? | SL-C005, SL-C007 | Five finalists, same scrambles; bar chart of times | What is the verdict? |
| S07 The Verdict | How big is the shared boost? | SL-C001 | Gauge showing ~2%; red line at 10% crossed out | What can't we tell? |
| S08 Limitations | What is missing from this picture? | SL-C075, SL-C076 | DNF icons; slot clock; "Personal luck" fog | What about the records? |
| S09 The Records | Does this apply to specific records? | SL-C104, SL-C105 | Record cards; "Aggregate result" disclaimer | How robust is the data? |
| S10 Robustness | Do the results hold up to checks? | SL-C037, SL-C038, SL-C046 | Era splits; leave-one-out solver bars; all-finalist share | Final summary. |
| S11 The Takeaway | So, is it luck? | SL-C001, SL-C005 | Recap of the 2% vs 10% verdict; "Shared component" label | End. |

## Script (v0)

### S01 The Belief

> When a world record falls, the first comment is often the same: "Lucky scramble?"
> In 2018, after Yusheng Du’s 3.47, Ruwix asked, "Lucky scramble? Maybe." [SL-C104]
> WIRED’s Robbie Gonzalez said, "The fact is, sometimes you just get a lucky scramble." [SL-C104]
> For Xuanyi Geng’s 3.05 in 2025, the same article said, "He got a lucky scramble," while also crediting smart choices. [SL-C107]
> It’s a compelling story. But is it true? And if so, how much?

### S02 The Scope

> Before we judge luck, let’s define the playing field.
> This study looks at 3×3 Rubik’s Cube finals from 2019 to 2025. [SL-C003]
> It covers 5,017 finals, 306,155 scheduled attempt slots, and 301,668 successful solves. [SL-C002]
> We are not asking, "Was Yiheng Wang’s 3.08 lucky?" [SL-C106]
> We are asking: How much does the scramble difficulty *shared by all finalists* speed up season-best final solves? [SL-C002]

### S03 The Basics

> Let’s quickly define the terms.
> A **scramble** is a random sequence of moves that sets the cube to a solved state. [SL-C132]
> A **cross** is the first step, solving the bottom face and its adjacent edges. [SL-C137]
> **CFOP** is the most common method: Cross, F2L, OLL, PLL. [SL-C138]
> A **PLL skip** happens when the cube is already in the correct orientation, saving an algorithm. [SL-C138]
> An **average of five** uses 5 attempts, discards the fastest and slowest, and averages the middle 3. [SL-C130]

### S04 The Obvious Answer

> The obvious way to check for luck is to look at a record reconstruction.
> Du’s 3.47 had an 8-token double extended cross. [SL-C137]
> Park’s 3.13 had a 13-token double extended cross and an 8-token OLL, plus a PLL skip. [SL-C138]
> These look easy. Short algorithms, skipped steps. It’s tempting to say, "That was just a lucky scramble."
> But here’s the problem: Luck that suits one solver is not luck everyone shares.

### S05 The Flaw

> Imagine two solvers, A and B, in the same final. They solve the same five scrambles.
> Solver A is fast on scramble 1, but slow on scramble 3.
> Solver B is slow on scramble 1, but fast on scramble 3.
> If you only look at A’s record, you might think scramble 1 was "lucky" for A.
> But B’s time on scramble 1 shows it wasn’t easy for everyone.
> The "luck" is relative to the solver, not the scramble itself.

### S06 The Fairer Test

> So how do we measure the *shared* component?
> We look at every finalist in a final. They all solve the same five scrambles.
> By comparing their times, we can estimate how much of the variance is due to the scramble/slot conditions shared by all.
> The shared scramble/slot component accounts for 4.7434% of balanced-tier within-solver-round successful log-time variance. [SL-C005]
> This is a measure of the *common* difficulty, not individual skill. [SL-C005]

### S07 The Verdict

> Now, let’s translate that variance into a time adjustment.
> The estimated shared-scramble-adjusted time is about 1.98% longer than observed. [SL-C001]
> In other words, the shared scramble/slot component is small, around 2% for these season bests. [SL-C001]
> The data rule out a shared boost as large as 10%. [SL-C001]
> The entire 95% interval lies below the registered 1.10 line. [SL-C001]
> So, while scrambles do matter, the *shared* luck is not a huge factor.

### S08 Limitations

> But let’s be honest about what this *can’t* tell us.
> First, slot conditions. The time slot a solver is in can affect their performance, and this is shared by all finalists in that slot. [SL-C057]
> Second, DNFs. We analyze successful solves; DNFs are handled separately. [SL-C075]
> Third, personal luck. If a solver gets a PLL skip in their own solution, that is personal luck, not shared. We cannot separate personal luck from execution. [SL-C076]
> The data cannot separate personal luck from execution. [SL-C076]

### S09 The Records

> So, does this apply to specific records?
> Not directly. This is an aggregate result. [SL-C001]
> We cannot say, "Yiheng Wang’s 3.08 was 2% luck." [SL-C106]
> We can say that, on average, across thousands of finals, the shared scramble/slot component is about 2%. [SL-C001]
> Exact-record stories require verified actual assignments and remain illustrative, not independent confirmations. [SL-C104]

### S10 Robustness

> Is this result robust?
> Yes. We checked it across eras. From 2019–2022, R is 1.0186. From 2023–2025, R is 1.0202. [SL-C037, SL-C038]
> We left out each year in turn; the result stays around 1.02. [SL-C039, SL-C040, SL-C041, SL-C042, SL-C043, SL-C044, SL-C045]
> We deleted each solver in turn; the result stays stable. [SL-C049, SL-C050]
> We compared all finalists; the common-only share is 4.4145%. [SL-C046]
> The verdict holds.

### S11 The Takeaway

> So, is a record solve "lucky"?
> The shared scramble/slot component is small, around 2%. [SL-C001]
> The data rule out a shared boost as large as 10%. [SL-C001]
> Luck exists, but it’s not the dominant factor. Skill, execution, and personal opportunities matter more.
> The next time someone says, "Lucky scramble?", you can say: "Maybe, but it’s only about 2% of the story." [SL-C001]

## Short 1 — The 2% Rule

> When a world record falls, people say, "Lucky scramble?"
> We measured the shared scramble/slot component across 5,017 finals from 2019–2025. [SL-C002]
> The result: it’s about 2%. [SL-C001]
> The data rule out a 10% boost. [SL-C001]
> Luck is real, but it’s a small part of the story. Skill matters more. [SL-C001]

## Short 2 — Why One Record Isn’t Enough

> Looking at one record reconstruction is misleading.
> Du’s 3.47 had an 8-token cross. [SL-C137]
> Park’s 3.13 had a PLL skip. [SL-C138]
> But luck that suits one solver isn’t luck everyone shares.
> We compare all finalists in a final to measure the *shared* difficulty. [SL-C005]
> That’s the fairer test. [SL-C005]
