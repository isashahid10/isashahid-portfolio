#!/usr/bin/env python3
"""
Generates /blog from the POSTS list below.

Run:  python3 tools/build_blog.py
Then: git add blog && commit

House rules enforced by check_output() at the bottom:
  - no em dashes anywhere (the author hates them)
  - no dates on posts
  - every post has a title, blurb, tags and body
"""

import html
import os
import re

SITE = "https://isashahid.netlify.app"
OUT = "blog"

# --------------------------------------------------------------------------
# POSTS.  body is light markup: blank-line separated blocks.
#   ## heading
#   - bullet
#   > quote
#   plain paragraph
# Inline: **bold**, `code`, [text](url)
# --------------------------------------------------------------------------

POSTS = [
{
"slug": "forking-someone-elses-code",
"title": "Forking someone else's code and immediately wanting to ruin it",
"blurb": "The first thing I wanted to do in the OpenStrap codebase was exactly the wrong thing, and the codebase would have let me.",
"tags": ["WHOOP", "Architecture", "Dart"],
"body": """
My WHOOP band is a nice piece of hardware that turns into jewellery when you stop paying. So I stopped paying and went looking for a way to keep the band.

That is how I ended up in [OpenStrap](https://github.com/OpenStrap), an open source project that had already done the genuinely hard part: working out what the band actually says over Bluetooth. I want to be upfront that this is a fork. I did not decode the protocol. Someone else did, and they did it properly.

## The part I did not expect

I assumed the interesting bit would be sensors and maths. It was not. It was the folder structure, which sounds like the most boring sentence ever written, so bear with me.

OpenStrap splits everything into three repos and refuses to let them bleed into each other:

- **protocol** takes bytes off the band and gives you named records. It knows about Bluetooth. It has no idea what a "recovery score" is.
- **analytics** takes those records and computes metrics. It knows the published methods. It has never heard of Bluetooth.
- **edge** is the app. Storage, screens, flows. It treats the other two as libraries and does not reach past them.

## Where I tried to be clever

Roughly ten minutes in, I wanted to add a feature that needed a value the analytics layer computes. The fastest path was obvious: have the UI grab a raw field straight out of the protocol layer and do the maths right there in the widget. Two minutes of work. Would have worked perfectly. Nobody would have known.

I did not do it, and it took me an embarrassingly long time to articulate why beyond "it feels wrong".

The reason is that the split is the only thing making the decoder testable on its own. The moment the UI knows what a Bluetooth characteristic looks like, you cannot verify the decoder without booting an app, and you cannot change the decoder without auditing every screen that might be reading those bytes. The boundary costs you two minutes today. What it buys is the ability to reason about one piece at a time forever.

> Working inside someone else's module boundaries is a completely different skill from drawing your own. You do not get to argue with the design. You have to understand why it is there before you have earned the right to be annoyed by it.

## What I actually added

The band knows how hard your body worked. It has no clue what you did. It sees your heart rate go up and cannot tell a heavy set of squats from a stressful email, which feels like a metaphor for something.

So my fork adds resistance training logging, nutrition tracking, weather context (heat moves both your heart rate and how bad you feel, and without it you misread yourself every summer), and AI summaries that are only useful because those three inputs exist.

All of it runs on the phone. No account, no sync, no server holding my heart rate. That was a constraint from day one rather than a feature I bolted on, and it deleted an enormous amount of work. No auth layer. No data retention policy. No monthly bill.

It is a personal build for one person and one band. It is not a product, there is no roadmap, and I am not pretending otherwise. It works, I use it daily, and I add things when I want them.

Code is at [github.com/isashahid10/whoop](https://github.com/isashahid10/whoop).
"""
},
{
"slug": "my-heart-rate-does-not-need-the-cloud",
"title": "My heart rate does not need to visit a data centre",
"blurb": "Working out how much of a fitness tracker genuinely requires a server. The answer is close to none of it, which raises an awkward question.",
"tags": ["WHOOP", "Privacy", "On-device"],
"body": """
Here is a question I did not think to ask for an embarrassingly long time: why does my fitness tracker need the internet?

Not "why does the company want it to". That one is easy. I mean technically. What part of turning a heart rate signal into a recovery number actually requires a machine in another country.

## Going through it honestly

Heart rate variability is arithmetic on the gaps between beats. Sleep staging is pattern recognition on signals the band already has. Strain and recovery are published, citable methods that people wrote papers about. Every one of these is maths on a stream of numbers that is already, physically, on your wrist.

A phone from five years ago can do all of that without noticing. There is nothing here that needs a GPU farm. There is nothing here that needs to leave the building.

So the cloud is not doing computation. It is doing billing.

## What changes when you decide it stays local

I built my fork on the assumption that nothing leaves the phone, and the surprise was how much work that deleted rather than added.

No accounts, so no signup flow, no password reset, no "verify your email" template I would have written badly. No sync, so no conflict resolution, and no bug where your phone and the server disagree about last Tuesday. No server, so no bill, no uptime worry, and no 2am problem that is mine. No data retention policy, because there is nothing retained anywhere I do not personally hold.

I had genuinely believed local-first would be the harder path. It was the lazier one. Turns out most of the complexity in a small app is not the feature, it is the machinery around synchronising the feature.

## The bit that is not lazy

Local-first is only free when the data is yours alone. The moment two people need to see the same thing, you need a server and all the misery that comes with it, and pretending otherwise gives you a worse server implemented badly inside your app.

So the honest version of this post is not "the cloud is a scam". It is: **work out whether your data is genuinely multiplayer before you build for multiplayer.** Mine is one person and one band. Yours might not be.

The best way to protect a piece of sensitive data is to never have collected it. The second best is for it to never leave the device it was created on. Both of those were available here and I would have missed them if I had started by drawing a backend.
"""
},
{
"slug": "hash-chains-are-just-receipts",
"title": "Hash chains are just receipts that grass on you",
"blurb": "CodeProof exists because 'I definitely wrote this myself' is not evidence, and I wanted to find out how little machinery it takes to make it evidence.",
"tags": ["CodeProof", "TypeScript", "Cryptography"],
"body": """
Academic integrity tooling mostly answers "does this look like something else". CodeProof, which is a VS Code extension I built, tries to answer a different question: **when was this written, and has it been quietly edited since.**

Those are not the same question and the second one turns out to be much easier.

## The whole idea in one paragraph

Hash a file. Store the hash. Hash the next snapshot together with the previous hash. Repeat. Now every record depends on the one before it, so if you go back and change something in the middle, every hash after it stops matching. You do not need to detect the edit. The chain detects it for you and cannot help itself.

That is it. That is the entire trick. It is the same idea underneath a lot of things that get described with far more excitement than it deserves.

## What I actually had to build

- Snapshot the workspace on a timer, so there is something to chain in the first place
- SHA-256 hash every snapshot against the previous one
- Store the whole event log locally in SQLite, because it never leaves your machine
- A replay player that scrubs back through a session like video
- A flag analyser that surfaces large pastes and odd jumps **for a human to review**, rather than accusing anyone of anything
- PDF report export, with the narrative written by Gemini
- A verification step that reports **exactly which file broke the chain and when**, because "verification failed" is a useless error message and I have received enough of those to know

That last one is the only part I would defend as design work rather than plumbing. An integrity tool that tells you something is wrong without telling you where is just anxiety with a progress bar.

## What it does not do

It does not prove you wrote the code. Nothing can. You could type someone else's work in by hand and the chain would happily certify that you typed it slowly.

What it proves is the shape of the process: that the work existed at a sequence of points in time, and that the record has not been retroactively tidied up. For an audit where the question is "did this appear fully formed at 2am the night before", that shape is the whole argument.

> Knowing the limits of what your tool proves is more important than the tool. Every so often someone builds an integrity system, forgets what it actually attests, and starts treating the output as truth.

## The bit I got wrong first

My first version stored hashes and nothing else, which felt clean and minimal and was completely useless. A hash on its own tells you a file changed. It cannot tell you a file changed **in a way that skipped steps**, because there is no notion of steps.

Chaining is what turns a pile of fingerprints into a story. Same primitive, one extra field, entirely different tool.

Code is at [github.com/isashahid10/codeproof](https://github.com/isashahid10/codeproof).
"""
},
{
"slug": "the-weather-is-a-distribution",
"title": "The weather is a distribution and everyone forgets",
"blurb": "STORMCAST came out of noticing that a forecast is a range of outcomes, and most people trading on weather are using a single number.",
"tags": ["STORMCAST", "Forecasting", "Electron"],
"body": """
If you ask your phone what tomorrow's high is, it says a number. One number. Twenty four degrees.

That number is a lie of omission. What the model actually produced was a spread of possible outcomes, and somebody picked the middle of it and threw the rest away because a range does not fit on a lock screen.

## Why that gap is interesting

The ECMWF ensemble runs the forecast 51 times with slightly different starting conditions. You get 51 answers. Sometimes they cluster tightly, which means the atmosphere is being predictable and you can be confident. Sometimes they spray across eight degrees, which means tomorrow is genuinely up for grabs and anyone quoting you a single number is guessing with extra steps.

Those two situations look identical if all you see is the average.

STORMCAST ingests the full 51 member ensemble for specific airport weather stations and builds an actual temperature distribution instead of a point estimate. The bet is that markets pricing weather outcomes are often anchored to the single-number city forecast, and the distribution knows something the headline does not.

## The architecture, which is a bit silly

Electron and Vite for the interface, Python for the forecasting work, talking to each other over a local socket bridge. A Node frontend and a Python bot sharing a port like flatmates.

Is this the architecture I would choose from scratch? Probably not. It happened because the forecasting and statistics ecosystem lives in Python and I was not going to reimplement it in JavaScript out of tidiness. Use the language that already has the libraries, then pay a small tax at the boundary. The tax was real but much smaller than the rewrite.

## Position sizing, or how to lose slower

Kelly optimal sizing is in there, and the honest reason is that the failure mode of a system like this is not being wrong. Being wrong is fine and expected. The failure mode is being right on average and still going broke because you bet too much on one thing at the wrong moment.

I also built it with paper trading and calibration analytics before anything else, which in hindsight is the only defensible order. **A signal you have not measured is a hunch with a user interface.** Calibration asks the uncomfortable question: when this thing said 70 percent, did it happen about 70 percent of the time? If you cannot answer that, you do not have a model, you have a mood.

## What I would tell past me

Build the scoreboard before you build the player. It is much less fun and it is the only way you ever find out if any of this works.
"""
},
{
"slug": "access-control-is-schema",
"title": "Access control is schema, not middleware",
"blurb": "The most expensive thing I got wrong on Docaroo was treating 'who can see this' as something to add after the feature worked.",
"tags": ["Docaroo", "Supabase", "Security"],
"body": """
I am technical co-founder of Docaroo, a telehealth platform that has seen around 1,500 patients. My co-founder is a practising GP. That combination has shaped my engineering more than any framework choice.

This post is about the thing I got wrong.

## The mistake

I built features first and thought about permissions second. Get the flow working, then add the check. That is how I had always done it, and on every previous project it was fine.

It is not fine when the row is a patient record.

The problem is not that you might forget a check, although you might. The problem is that **who can read a field determines how you store it**, and by the time you notice, you have written queries against a shape that assumed the answer did not matter. Retrofitting permissions is not adding an `if`. It is rewriting things you already shipped and re-testing paths you thought were done.

## What I do now

For every new field, three questions before the migration:

- Who needs to **read** this?
- Who needs to **write** it?
- What is the smallest set of people for whom either answer is yes?

The useful part is that the honest answer is almost always fewer people than the convenient design assumes. Convenience says "the clinician dashboard needs the patient object". The honest answer is usually "the dashboard needs four fields off the patient object", and those are very different rows to protect.

> The best way to protect sensitive data is to never have collected it. The second best is for very few code paths to be able to reach it. Everything after that is damage control with good intentions.

## Blast radius

The other thing that changed is how I think about deploying. A broken flow in a side project means somebody is annoyed. A broken flow here means a person who needed a medical certificate for work does not get one, or a consultation drops halfway through while somebody is describing a symptom.

What that actually changed in practice was narrower than "be careful", which is useless advice. It was that the consultation path stopped being somewhere I experiment. Dashboards, onboarding copy, pricing presentation: still fast, still iterate. The path from "patient books" to "patient has what they came for" does not change casually and does not change late on a Friday.

Two speeds in one codebase, and being explicit about which one you are in.
"""
},
{
"slug": "boring-technology-is-a-feature",
"title": "Boring technology is a feature you ship to yourself",
"blurb": "Docaroo runs on the least interesting stack I could assemble, on purpose, and it is the best decision I made.",
"tags": ["Docaroo", "Next.js", "Pragmatism"],
"body": """
The Docaroo stack is Next.js, Supabase, Daily.co for video, Stripe for payments. If that sounds like it was chosen by someone who wanted to go home on time, correct.

There is nothing clever in it. That is the point, and it took me a while to be at peace with that.

## Complexity budget

You get a fixed amount of complexity you can hold in your head. Everything you spend on infrastructure is not available for the domain, and in a domain like healthcare the domain is where all the actual difficulty lives.

Every hour I would have spent being interesting about the database is an hour not spent working out what happens when a consultation drops out halfway, or how a certificate should be generated, or what a clinician needs on screen while they are also talking to a human being.

Nobody has ever booked a telehealth appointment because of the ORM.

## The bill is a teacher

I own the infrastructure spend, which turns out to be an extremely effective form of education. When it is your card, you stop reaching for the managed service that costs 200 a month to save you a day of work.

You also get honest fast about what the product needs versus what would be nice. Nice things have a price now. It is remarkable how many architectural opinions evaporate when they are itemised.

## Where I do spend

Video and payments are both bought, not built, and I will defend that forever. Both are areas where being 95 percent correct is worth nothing. A video call that works most of the time is a broken product. A payment flow that is nearly right is a support nightmare and possibly a legal one.

**Build the thing that is your actual product. Buy the things where the failure mode is somebody else's specialty.**

## The uncomfortable bit

Boring is not the same as easy, and I want to be careful not to make this sound wiser than it is. The stack being dull does not mean the work is dull. It means the difficulty is concentrated where it should be, which is in understanding the problem rather than in operating your own infrastructure.

If anything the boring stack raises the standard, because you no longer get to be pleased with yourself about the plumbing. The plumbing works. Now go and do the hard part.
"""
},
{
"slug": "two-losses",
"title": "Two thousand dollars of tuition, paid to two German cars",
"blurb": "The worst deals we ever did taught me more than every good one, and not for the reason people usually say that.",
"tags": ["Yakiamotors", "Decisions", "Risk"],
"body": """
We started Yakiamotors with 3,200 dollars borrowed between three of us. Over 35 or so flips that turned into roughly a 38,000 dollar capital base.

That is the number that goes on a CV. It is also the least interesting thing about the business, because it is an output. The thing that produced it was a decision we only made because we lost money twice in a row.

## The thesis that felt clever

We liked high mileage German cars early on, and the logic was genuinely reasonable. Ten year old European sedan, badge still carries perceived value, depreciation has already done its worst, nervous private sellers, wide spread between what you pay and what it lists for.

What that logic quietly ignores is that the spread is wide **for a reason**, and the reason is that the repair bill on those cars is not a number you can estimate. It is a distribution with a long ugly tail. Usually a few hundred dollars. Occasionally a suspension component or an electronic module turns a 600 dollar tidy up into a 2,000 dollar problem, because the specialist parts that make the car desirable are the same parts that make it expensive to fix.

We lost over a thousand on one. Then we lost over a thousand on the next.

## Two is not a pattern, except when it is

Here is the part I still think about. Two losses is not statistically meaningful. If you showed me somebody else's two bad deals I would say variance, keep going, and I would be giving defensible advice. Plenty of businesses die from panicking at a small sample.

What made it a signal was not the count. It was that both losses had the **same shape**. Purchase price fine. Valuation fine. Margin killed by a repair cost we could not have bounded before buying.

So the failure was not bad luck twice. It was that our model had a term in it that we were treating as an estimate when it was actually a random variable with a fat tail.

> You do not need a big sample to act when the failures share a mechanism. Two losses from the same cause is a completely different signal to two losses from different causes.

That reframe is what let us move fast without kidding ourselves. We were not concluding "German cars bad". We were concluding "our margin model is wrong wherever repair cost has high variance", and those cars were just the clearest example.

## The pivot

We moved to Japanese make city cars. Less glamorous, thinner headline spreads, and a gloriously boring repair distribution. Commodity parts, standard labour, worst case close to average case.

Margins after that ran 20 to 65 percent. Not because Japanese cars are magic. Because we stopped taking a risk we were not being paid for and could not measure.

## Where it shows up now

I think about the fat tail thing constantly and it has nothing to do with cars. Any estimate you treat as a single number when it is really a distribution will eventually take a bite out of you, and it will pick its moment.

A build that "usually takes two days". A dependency upgrade that is "probably fine". The average is not what hurts you. The tail is.
"""
},
{
"slug": "i-built-a-tool-because-i-was-annoyed",
"title": "I specced a whole product because I was annoyed at a group chat",
"blurb": "FlipIQ exists because the information needed to spot our worst pattern was sitting in three people's heads and nowhere else.",
"tags": ["Yakiamotors", "FlipIQ", "Product"],
"body": """
After we pivoted the car business, the thing that bothered me was not the money. It was how long it took to notice.

The pattern was there in the data. It just was not anywhere you could look at it. It was spread across three people's memories, a group chat, and a spreadsheet somebody updated when they felt like it. Nobody was tracking outcomes by category, so the only way to spot a bleeding category was for one person to have a feeling and be brave enough to say it out loud.

That is a terrible detection system and it cost us two thousand dollars.

## What FlipIQ is

A deal scoring tool with four pieces:

- **Listing alert engine**, because the good deals are gone in hours and refreshing a website is not a strategy
- **Automatic comparison against Carsales market valuations**, so a price is scored against something rather than against vibes
- **Kanban pipeline** for cars in progress, because three people and six cars is genuinely more state than a human tracks reliably
- **Flip analytics database**, which is the actual point

The first three are convenience. The fourth is the one that exists so the next time a category is quietly losing us money, it shows up as a number instead of a hunch.

## Prioritising it honestly

I ranked the backlog with RICE, and the spec was driven by analysis of 35 or so real flips rather than a wishlist. That distinction matters more than the framework does. RICE is arithmetic. It is only as good as whether your reach and impact numbers came from anywhere real.

Doing it against actual flip data changed the order. Things I was excited to build turned out to affect two deals a year. The boring database that nobody would demo turned out to be the thing that would have caught the pattern.

## The general version

**Most tools worth building come from noticing that you keep doing something badly, not from noticing a gap in a market.**

I did not do market research and conclude that car flippers need software. I got annoyed, twice, at the same missing piece of information. That is a much better signal, because it comes with a guaranteed first user who is definitely motivated, which is me.

The failure mode of this approach is building something only you want. The saving grace is that you find that out cheaply, and the tool is still useful to you, which is more than most side projects manage.
"""
},
{
"slug": "my-face-was-600kb",
"title": "My face was 600KB and other crimes against my own website",
"blurb": "I rebuilt this site and then measured it, in that order, which was the wrong order.",
"tags": ["This site", "Performance", "Web"],
"body": """
I rebuilt this website recently. Nicer type, proper dark mode, animations that are not embarrassing. I was quite pleased.

Then I measured it. The homepage was **1,042 KB**. Of that, **627 KB was a single photo of my face**, displayed at 188 pixels wide, stored as an 800 pixel PNG.

PNG. For a photograph. Of a person.

## The fix took four minutes

Resize to 400 pixels, which is still 2x for a retina display. Convert to WebP with a JPEG fallback. Result: **8.5 KB**. That is 99 percent smaller and I could not tell the difference with the two versions side by side.

Total homepage went from 1,042 KB to 104 KB. One image. Four minutes. Ten times faster.

## The genuinely embarrassing part

The image was in a folder called `Certificates`. It had been sitting there since the first version of the site because that is where I dumped it once and never thought about again. Nobody audits their own assets folder. It is the junk drawer of software.

## Things I have now learnt the hard way

**PNG is for graphics with flat colour and sharp edges.** Logos, icons, screenshots of text. A photograph in PNG is storing every single skin tone gradient losslessly for absolutely no reason.

**Measure before you are proud.** I spent real time on easing curves and letter spacing while shipping two thirds of a megabyte of my own head. The taste work was not wasted, but it was polishing the paintwork on a car with no wheels.

**Nothing tells you.** No error, no warning, no lint rule. The site worked. It looked fine on my machine on my wifi. The only way you find out is if you go looking, and the only reason to go looking is if you have decided that this is a thing you check.

## The rest of the audit, since I was already there

While I was in the mood: no favicon, so every tab showed a blank page icon. No Open Graph tags, so every time I pasted my own link into a message it rendered as a grey rectangle with no image, which is a strange thing to be doing while asking people to look at your work.

Both are twenty minute fixes that had been broken for months. The lesson is less about images and more about the fact that **the things nobody complains about are the things nobody checks.**
"""
},
{
"slug": "solo-projects-did-not-prepare-me",
"title": "Nothing about solo projects prepared me for a real process",
"blurb": "Everything I had built before, I was the only person who had to agree with me. That turns out to have been doing a lot of work.",
"tags": ["Boeing", "Engineering", "Learning"],
"body": """
I am doing an Industry Based Learning placement as a software engineering intern, working on factory systems. It is the first time I have written code inside an established engineering process rather than one I invented for myself that morning.

I am not going to write about anything internal here. This is only about the adjustment, which was bigger than I expected.

## What solo projects teach you badly

On my own projects I am the architect, the reviewer, the tester and the only person who has to be convinced. I had started to believe this made me fast.

It made me fast at the parts I find easy. It also meant every one of my habits had gone completely unchallenged, because there was nobody in a position to challenge them. My commit messages were for me. My branch names were for me. My "obvious" naming was obvious to exactly one person, and that person had the full context in his head at the time and would not have it two weeks later.

## Code review is a different sport

The first time somebody reviews your code properly is a humbling afternoon. Not because the feedback is harsh, but because the questions are ones you never had to answer.

Why this name. What happens if this is empty. Is this the same as the thing over there, and if it is, why is it written differently. On a solo project all of those have the same answer, which is "because that is how I felt at the time", and that answer does not survive being said out loud.

The useful reframe I have landed on: **review is not somebody checking your work. It is somebody testing whether the code explains itself to a person who was not there when you wrote it.** That is a property of the code, not a property of you, which makes it much less personal and much more fixable.

## Traceability is not bureaucracy

I came in with a mild private opinion that process is what happens when organisations get too big to move. I have revised this.

When correctness genuinely matters and other people depend on what you shipped, the ability to answer "why is this like this, who decided, and when" is not overhead. It is the thing that lets anyone change the system later without being afraid. Version control and release process are not there to slow you down. They are there so that a change six months from now is a decision rather than a gamble.

## The honest summary

I was good at the part where you build a thing. I was inexperienced at every part that comes after, which it turns out is most of the job. That is a genuinely useful thing to find out at 20 rather than at 30.
"""
},
{
"slug": "explaining-recursion-to-a-nine-year-old",
"title": "Explaining recursion to a nine year old, badly, then well",
"blurb": "Teaching kids to code is the fastest way to find out which things you understand and which things you have only memorised.",
"tags": ["CodeCamp", "Teaching", "Learning"],
"body": """
I teach Python, game design and robotics to kids aged 7 to 16. Usually eight or so per session, all at different levels, several of whom would rather be somewhere else.

It is the single most useful thing I have done for my own understanding, and not for the reason people usually give.

## Kids cannot be fobbed off

An adult who does not follow your explanation will nod. They will fill the gap later, or quietly decide it does not matter, or assume the problem is them. You get away with it.

A nine year old will look at you and say "but why though", and they will keep saying it, and they are not being difficult. They are correctly identifying that you have not actually explained anything, you have just said true sentences in a confident voice.

This is a brutal and excellent test. **You find out very quickly which concepts you understand and which ones you have memorised the shape of.**

## My first attempt at recursion

I said something like "it is a function that calls itself". Which is true, and useless, and I watched it land as absolutely nothing.

What worked was much dumber. Stand at the back of a queue. You want to know what position you are in. You cannot see the front. So you tap the person ahead and ask what number they are, and they do not know either, so they tap the person ahead of them, and this keeps happening until it reaches someone at the very front who says "I am number one" because they can see there is nobody ahead. Then the answer comes back down the queue, everyone adding one.

The base case is the person at the front. The stack is the queue. Nobody in the middle knows the answer and nobody in the middle needs to.

That got it. It got it because it has a **why does it stop** built into the story, and "a function that calls itself" does not, which is exactly why beginners write infinite loops.

## What transferred

I now think the test of understanding something is whether you can explain it without using its vocabulary. If I can only describe recursion using the words "recursion", "stack" and "base case", I have learnt the labels.

The other thing, which took longer: **an explanation that fails is information about the explanation, not about the listener.** My instinct the first few times was to conclude the kid was not getting it. The kid was fine. The queue metaphor was sitting there the whole time and I had not gone looking for it.

I have started applying this to documentation and code review and, occasionally, to arguments.
"""
},
{
"slug": "forty-tickets-a-week",
"title": "What forty support tickets a week does to your brain",
"blurb": "The best product research I have ever done was a job I did not think of as product research at the time.",
"tags": ["Global Fitness", "Operations", "Product"],
"body": """
For a while I was resolving 40 plus customer issues a week across NetSuite, eBay and Amazon. Order problems, returns, things that arrived broken, things that arrived fine but were not what somebody thought they ordered.

At the time I thought of it as a job. In hindsight it was the most concentrated exposure to real user behaviour I am ever likely to get.

## Individual tickets lie, the pile does not

Any single complaint is noise. Somebody had a bad day, somebody misread a listing, somebody is wrong. If you respond to tickets one at a time you learn nothing and you slowly develop the belief that customers are idiots, which is both wrong and a career limiting worldview.

Two hundred a month is different. At that volume the same complaint keeps arriving in slightly different words, and you stop seeing individual annoyed people and start seeing **the specific place where the product and reality disagree**.

That is not a support insight. That is a product insight that happens to be arriving through the support queue.

## Bringing it to the meeting

I started presenting pattern level findings at weekly sales meetings rather than ticket counts. Not "we had 200 issues", which is a number nobody can act on. More like: this category generates returns at a rate the others do not, and here is the specific reason people give.

Return rates came down about 12 percent. I want to be careful not to claim all of that, because other people changed other things too. But the mechanism was real and it was not clever. It was just that the information existed in the support queue and had never been aggregated and walked upstairs.

## The thing I actually took away

**The people closest to the failures are usually the furthest from the decisions.** Support knows exactly what is broken. Support is rarely in the room where the roadmap gets set, so what they know arrives, if at all, as a vague sense that customers are unhappy.

Closing that gap did not require a system or a tool. It required somebody to count, and to turn up.

The other thing, which I am less proud of: I had to consciously fight the drift towards contempt. When you handle the same avoidable problem forty times, it is very easy to conclude that people are careless. The more useful conclusion, almost always, is that something is designed so that a normal person makes that mistake. Blaming the user is comfortable and it terminates the investigation.
"""
},
{
"slug": "i-am-not-a-designer",
"title": "I am not a designer but I did read the manual",
"blurb": "What I learnt rebuilding this site about animation, and specifically about when the correct amount of animation is none.",
"tags": ["This site", "Design", "Animation"],
"body": """
I rebuilt this site properly, which meant reading actual material on interface design instead of copying whatever looked nice on someone else's page.

Here is what stuck, mostly from Emil Kowalski's writing on animation and Apple's talks on fluid interfaces.

## The question nobody asks first

The first question is not "what animation should this have". It is **"should this animate at all"**, and the answer is often no.

The rule that reorganised my thinking is about frequency. Something a user sees a hundred times a day should never animate, because you are adding delay to an action they have already decided on. Something they see occasionally can animate. Something they see once, like a first load, is where you are allowed to have fun.

Raycast has no open animation. That is not laziness, that is the correct answer for something you open forty times a day.

## Easing, or why your dropdown feels slow

`ease-in` starts slow. Which means it delays movement at exactly the moment the user is watching hardest, right after they clicked. A dropdown with `ease-in` at 300ms **feels** slower than the same dropdown with `ease-out` at 300ms, despite being identical in duration.

Also: the built in CSS easings are weak. `cubic-bezier(0.23, 1, 0.32, 1)` is what I use for most things now and it has an actual snap to it.

## Small rules, large effect

- Never animate from `scale(0)`. Nothing in reality appears from literally nothing. Start at `scale(0.95)` with opacity and it reads as arriving rather than materialising.
- Buttons need `transform: scale(0.97)` on `:active`. It costs one line and it is the difference between an interface that responds and one that merely works.
- Exits should be faster than entrances. You have already decided to leave.
- `transition: all` is a trap. Name the properties.
- Only animate `transform` and `opacity` if you can help it. They skip layout and paint. Animating height or margin makes the browser redo everything, every frame.

## The one that actually changed my behaviour

Gate hover effects behind `@media (hover: hover) and (pointer: fine)`.

Touch screens fire hover on tap. Without that gate, every hover animation you wrote fires on mobile at the exact moment somebody is trying to press the thing, and it feels broken in a way nobody can quite describe.

I had shipped this bug on every site I had ever made and had never once noticed, because I tested on a laptop like a fool.

## The meta lesson

None of this is talent. It is a list. Someone wrote the list down, I read it, and my interfaces got noticeably better within a day.

I had vaguely assumed design sense was something you either had or did not. A lot of it is just knowing about twenty specific things, most of which have a correct answer that somebody has already worked out and published for free.
"""
},
{
"slug": "things-i-believed-that-were-wrong",
"title": "Things I believed that turned out to be wrong",
"blurb": "A running list, kept mainly so I stop repeating myself.",
"tags": ["Learning", "Opinions"],
"body": """
A running list. Some of these were expensive.

## That local-first would be harder

I assumed building without a backend was the ascetic option, more work for ideological reasons. It deleted an enormous amount of work instead. No auth, no sync conflicts, no bill, no retention policy. The complexity was never the feature, it was the machinery around synchronising the feature.

Caveat: this only holds when the data genuinely belongs to one person. Get that wrong and you build a worse server inside your app.

## That two data points cannot be a pattern

They can, if the failures share a mechanism. Two losses from the same cause is a completely different signal to two losses from unrelated causes. I lost about two thousand dollars learning to tell those apart.

## That process was for big slow companies

Version control discipline, code review, release process. I thought these were things that happen to organisations when they stop being able to move. They are what makes a change six months later a decision instead of a gamble. I was confusing "I do not need this yet" with "this has no value".

## That being fast was a property of me

It was mostly a property of being the only person who had to agree with me. Take that away and a lot of my speed turns out to have been unexamined habit that only worked because I held all the context in my head and never had to hand it over.

## That the user was being careless

When the same avoidable mistake arrives forty times, the mistake is designed in. Blaming the user is comfortable and it stops the investigation dead, which is precisely why it is so appealing.

## That design sense was innate

It is substantially a list of about twenty specific things that people have already worked out and published. I read some of it and my work got better in a day. That is not talent, that is homework I had not done.

## That I should optimise the computation

I spent a while making maths faster when the actual problem was doing three unnecessary passes over the data. Ask what shape the work is before you ask how fast each piece runs.

## That an explanation failing says something about the listener

It says something about the explanation. A nine year old taught me this, repeatedly, by asking "but why though" until I found a better metaphor.

## That measuring could wait

I shipped a 600 KB photo of my own face and spent that same week fine tuning easing curves. Nothing warns you. The site works. The only way you find out is deciding it is a thing you check.
"""
},
]

# --------------------------------------------------------------------------

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'<a href="{m.group(2)}"'
                         + (' target="_blank" rel="noopener noreferrer"' if m.group(2).startswith('http') else '')
                         + f'>{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t


def render_body(body):
    out, buf = [], []
    for block in [b.strip() for b in body.strip().split("\n\n") if b.strip()]:
        lines = block.split("\n")
        if block.startswith("## "):
            out.append(f"<h2>{inline(block[3:].strip())}</h2>")
        elif all(l.strip().startswith("- ") for l in lines):
            items = "".join(f"<li>{inline(l.strip()[2:])}</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
        elif block.startswith("> "):
            q = " ".join(l.strip()[2:] for l in lines)
            out.append(f"<blockquote><p>{inline(q)}</p></blockquote>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n        ".join(out)


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{desc}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" content="#ffffff" id="themeColor">
    <title>{title} | Isa Shahid</title>
    <link rel="canonical" href="{canon}">
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
    <meta property="og:type" content="{ogtype}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{canon}">
    <meta property="og:image" content="{site}/assets/og.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{site}/assets/og.png">
    <link rel="stylesheet" href="/assets/post.css">
    <script>
        (function () {{
            var s = null;
            try {{ s = localStorage.getItem('theme'); }} catch (e) {{}}
            document.documentElement.setAttribute('data-theme',
                s || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
        }})();
    </script>
</head>
<body>
    <div class="topbar">
        <div class="wrap topbar-inner">
            <a href="{back}" class="back">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                {backlabel}
            </a>
            <button class="theme-toggle" id="themeToggle" aria-label="Switch theme">
                <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><line x1="12" y1="1.8" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22.2"/><line x1="4.4" y1="4.4" x2="5.9" y2="5.9"/><line x1="18.1" y1="18.1" x2="19.6" y2="19.6"/><line x1="1.8" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22.2" y2="12"/><line x1="4.4" y1="19.6" x2="5.9" y2="18.1"/><line x1="18.1" y1="5.9" x2="19.6" y2="4.4"/></svg>
            </button>
        </div>
    </div>
"""

FOOT = """
    <script src="/assets/theme.js"></script>
</body>
</html>
"""


def build():
    os.makedirs(OUT, exist_ok=True)

    for p in POSTS:
        canon = f"{SITE}/{OUT}/{p['slug']}.html"
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in p["tags"])
        page = HEAD.format(title=html.escape(p["title"]), desc=html.escape(p["blurb"]),
                           canon=canon, site=SITE, ogtype="article",
                           back="/blog/", backlabel="Blog")
        page += f"""
    <article class="wrap">
        <span class="eyebrow">Blog</span>
        <h1>{html.escape(p['title'])}</h1>
        <p class="standfirst">{inline(p['blurb'])}</p>
        <div class="tags">{tags}</div>

        {render_body(p['body'])}

        <div class="post-foot">
            <a href="/blog/">Back to all posts</a>
        </div>
    </article>
"""
        page += FOOT
        with open(f"{OUT}/{p['slug']}.html", "w", encoding="utf-8") as f:
            f.write(page)

    # ---- index ----
    cards = []
    for p in POSTS:
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in p["tags"][:2])
        cards.append(f"""            <a class="entry" href="/{OUT}/{p['slug']}.html">
                <h2>{html.escape(p['title'])}</h2>
                <p>{inline(p['blurb'])}</p>
                <div class="tags">{tags}</div>
            </a>""")

    idx = HEAD.format(title="Blog", desc="Notes on things I have built, things that broke, and things I was wrong about.",
                      canon=f"{SITE}/{OUT}/", site=SITE, ogtype="website",
                      back="/", backlabel="Isa Shahid")
    idx += f"""
    <main class="wrap">
        <span class="eyebrow">Blog</span>
        <h1>Blog</h1>
        <p class="standfirst">
            Notes on things I have built, things that broke, and things I turned out to be
            wrong about. {len(POSTS)} posts, no particular order.
        </p>

        <div class="entries">
{chr(10).join(cards)}
        </div>
    </main>

    <style>
        .entries {{ display: grid; gap: 2px; margin-bottom: 80px; }}
        .entry {{
            display: block;
            padding: 22px 20px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            text-decoration: none;
            color: inherit;
            transition: transform 180ms cubic-bezier(0.23,1,0.32,1), border-color 180ms ease, background-color 180ms ease;
        }}
        .entry h2 {{ margin: 0 0 8px; font-size: 1.0625rem; letter-spacing: -0.014em; }}
        .entry p {{ margin: 0 0 12px; color: var(--text-muted); font-size: 0.9375rem; line-height: 1.55; }}
        .entry .tags {{ margin: 0; }}
        .entry:active {{ transform: scale(0.995); }}
        @media (hover: hover) and (pointer: fine) {{
            .entry:hover {{ transform: translateY(-2px); border-color: var(--border-strong); background: var(--bg-subtle); }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .entry, .entry:hover, .entry:active {{ transform: none; }}
        }}
    </style>
"""
    idx += FOOT
    with open(f"{OUT}/index.html", "w", encoding="utf-8") as f:
        f.write(idx)

    return len(POSTS)


def check_output(n):
    bad = []
    for fn in os.listdir(OUT):
        txt = open(f"{OUT}/{fn}", encoding="utf-8").read()
        for needle, label in [("—", "em dash"), ("&mdash;", "&mdash; entity")]:
            if needle in txt:
                bad.append(f"{fn}: contains {label}")
    slugs = [p["slug"] for p in POSTS]
    if len(set(slugs)) != len(slugs):
        bad.append("duplicate slugs")
    return bad


if __name__ == "__main__":
    n = build()
    problems = check_output(n)
    print(f"built {n} posts + index into ./{OUT}/")
    print("checks:", "; ".join(problems) if problems else "clean (no em dashes, no dates, unique slugs)")
