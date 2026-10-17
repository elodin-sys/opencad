Source URL: https://zoo.dev/docs/faq
Title: Frequently Asked Questions

# Frequently Asked Questions

## Platform Overview

### Getting Started With Zoo Design Studio

#### What is Zoo Design Studio?

Zoo Design Studio is a unified Hybrid CAD platform built on our proprietary geometry engine. It combines AI-driven generation and editing of boundary-representation CAD models with familiar sketch and feature tree workflows, brings code to CAD through KCL, and includes Zookeeper, our conversational AI agent.

#### Is Zoo Design Studio available in a web browser or an installed application?

Zoo Design Studio is available as a desktop application and in a web browser. On desktop, you can keep projects in a local Directory library or in Personal Cloud. The browser uses Personal Cloud. See [Project Libraries](/docs/zoo-design-studio/features/data-management/project-libraries) for the differences.

#### How do I download Zoo Design Studio?

Visit our [downloads page](/design-studio/download) to install the desktop application.

#### How much does Zoo Design Studio cost?

Zoo Design Studio is available for free, and the Free plan includes {{pricing.free.included_usage_minutes}} of Zookeeper reasoning time. We have paid tiers that include additional Zookeeper reasoning time. You can [view our pricing here](/zoo-pricing).

#### Do I need a traditional CAD license to use Zoo Design Studio?

No. Zoo Design Studio is CAD software that anyone can use and download for free. Paid subscription tiers offer additional plan-specific features and capabilities. Visit our [pricing page](/zoo-pricing) for current details.

#### Does Zoo Design Studio require an internet connection?

An internet connection is required for modeling, rendering, Zookeeper, and syncing projects with Personal Cloud. Keeping a project in a local Directory library does not make Zoo Design Studio an offline CAD application.

### Core Features

#### What CAD modeling features does Zoo Design Studio have?

Zoo Design Studio has solid modeling features like extrude, sweep, loft, revolve, shell, hole, booleans, etc. For a full list of features, [visit our documentation](/docs/zoo-design-studio/features).

#### Does Zoo Design Studio support assemblies?

Yes. Assemblies have been supported in Zoo Design Studio since v1.0. However, Assembly Mates are still on our [roadmap](/roadmap).

#### How often is Zoo Design Studio updated?

We constantly ship updates to Zoo Design Studio. We do not currently follow a scheduled release cadence, which allows us to release exciting features and bug fixes as quickly as we can. To get a better idea of upcoming releases, check out Zoo's [roadmap](/roadmap).

#### What file types can I import into Zoo Design Studio?

See [Supported Import Formats](/docs/zoo-design-studio/features/data-management/import#supported-import-formats) for the current file extensions, support status, and import behavior. Formats under active development are explicitly labeled Experimental.

#### What file types can I export from Zoo Design Studio?

See [Supported Export Formats](/docs/zoo-design-studio/features/data-management/export#supported-export-formats) for the formats currently available from Zoo Design Studio and guidance on choosing one.

### Project Storage & Sync

#### Where are my projects saved, and can I keep them local?

On desktop, a Directory library keeps projects in a folder you choose on your computer. Personal Cloud stores projects in your Zoo account and keeps a working copy on the device where you open them. Cloud Sync keeps Personal Cloud projects up to date across devices.

Adding a Directory library does not upload its projects. Projects stay in that library unless you move them to Personal Cloud or publish them to Aquarium, which also moves them to Personal Cloud. Local project storage is separate from modeling: Zoo Design Studio still uses cloud services to run your code and render models. See [Project Libraries](/docs/zoo-design-studio/features/data-management/project-libraries).

#### How do I open a project on another device?

Create the project in Personal Cloud or use "Move to library" to move a Directory project there. With Cloud Sync enabled, wait for "Cloud synced" before switching devices. Sign in with the same Zoo account on the other device or in the browser, then open the project from Personal Cloud.

#### Which files does Cloud Sync upload?

Cloud Sync uploads your KCL code, project metadata, and other project files, including binary files, unless they are excluded. It respects project .gitignore rules and excludes version-control metadata such as .git, Zoo internal metadata, and generated project thumbnails. The .gitignore files themselves are uploaded.

Cloud Sync does not detect secrets in your files. Exclude sensitive paths before syncing. Keep a separate copy of important excluded files or local Git history: updates to the managed cloud working folder can remove them. See [Which Files Sync?](/docs/zoo-design-studio/features/data-management/cloud-sync#which-files-sync) for details.

#### Is Cloud Sync a backup or version-control system?

No. Cloud Sync keeps the current project available across your devices; it does not provide version history, branches, or a way to recover earlier revisions. Keep separate backups, and use a Directory library with Git if you need a version-control workflow.

#### What happens if I edit the same project on two devices?

Cloud Sync is not live collaboration. It can combine some independent file changes, but conflicting edits can require you to choose the local or cloud version for the whole project. Wait for "Cloud synced" before switching devices. If you see "Cloud conflict", review the differences and preserve any work you need before choosing a version. See [Resolve a Conflict](/docs/zoo-design-studio/features/data-management/cloud-sync#resolve-a-conflict).

#### Can I stop syncing a project and keep a local copy?

On desktop, use "Move to library" to move the project from Personal Cloud to a Directory library. Download the project first if it is cloud-only, and keep Cloud Sync enabled for the move. Turning Cloud Sync off only pauses synchronization; it does not remove the cloud copy.

Moving out of Personal Cloud permanently deletes the remote project and any Aquarium publication backed by it, while preserving and moving the selected local folder. The cloud project will no longer be available in the browser or on other devices. Back up important work before moving it. See [Stop Syncing](/docs/zoo-design-studio/features/data-management/cloud-sync#stop-syncing).

#### What happens when I delete a project from Personal Cloud?

Deleting from Personal Cloud deletes the cloud project, its local working copy on the current device if one exists, and any Aquarium publication backed by that project. The deletion propagates to other devices and has no undo. Read the confirmation dialog and keep a separate backup of anything you need. See [Delete a Synced Project](/docs/zoo-design-studio/features/data-management/cloud-sync#delete-a-synced-project).

### Zookeeper In Zoo Design Studio

#### How does Zookeeper fit into Zoo Design Studio?

Zookeeper is the AI CAD agent built into Zoo Design Studio. It can create and edit parametric CAD models from prompts, images, and sketches.

#### How do I open Zookeeper?

Click the sparkles icon in the right control bar. Zookeeper opens as a pane alongside your active project, where it can use your model, selections, renders, and KCL as context.

#### How can I learn more about Zookeeper?

Visit the [Zookeeper FAQs](/zookeeper#faq-general-overview) to learn more about its capabilities, workflows, and limitations.

### KCL & Code-Based CAD Design

#### What is KCL and what is it used for?

KCL (KittyCAD Language) is Zoo's own scripting language for describing CAD geometries and rendering them within Zoo Design Studio. Every CAD function in Zoo Design Studio generates KCL. Using KCL in Zoo Design Studio is completely optional and is not required. KCL allows designers to leverage the benefits of code in the CAD ecosystem. Learn more by reading our [KCL book](https://zoo.dev/docs/kcl-book/intro.html).

#### Do I need to know how to code in KCL to use Zoo Design Studio?

No! Coding with KCL (Zoo's CAD coding language) is completely optional. However, it can be quite powerful. If your curiosity gets the best of you, you can learn more about getting started with KCL for coding in CAD on our [Community Page](https://community.zoo.dev/).

### Developer Tools

#### Is Zoo Design Studio Open Source?

Yes, the Zoo Design Studio application is open source and you can [find it on GitHub](https://github.com/KittyCAD/modeling-app). However, our CAD geometry engine is not open source.

#### I want to build a custom CAD application with Zoo's APIs, where can I start?

Check out our [developer documentation](/docs/developer-tools) to get started designing your own modeling tools.

### Support & Updates

#### Where can I go if I need help?

Anyone can ask questions, discuss workflows, and get help through our [Community Forum](https://community.zoo.dev/) or [Discord](https://discord.gg/JQEpHR7Nt2). Paid customers who are signed in can also [submit a private support ticket](/contact?type=support) for issues that need direct assistance.

#### I found a bug. Where can I report it?

You can report bugs through our [Community Forum](https://community.zoo.dev/) or [Discord](https://discord.gg/JQEpHR7Nt2). For Zoo Design Studio bugs, you can also [open a GitHub issue](https://github.com/KittyCAD/modeling-app/issues). Please include reproduction steps, screenshots, logs, or example files when possible. Paid customers who need private assistance can also [submit a support ticket](/contact?type=support) while signed in.

#### How do I update Zoo Design Studio?

If an update is needed, a notification will appear the next time you open Zoo Design Studio. Once the update is complete, you will need to restart your application for it to take effect. You can also click "Settings" in the bottom toolbar, click to the "About" section, and view your current version or check for updates.

#### I have a feature request, where can I tell the team?

You can use our [Community Page](https://community.zoo.dev/) to see if someone else has requested the same thing. If no one has, make a new request using the feature category.

## Zookeeper

### General Overview

#### What is Zookeeper?

Zookeeper is an AI agent for CAD built into Zoo Design Studio. It turns text prompts, images, and sketches into real, parametric CAD models.

Describe your goals and constraints, then delegate tasks such as creating geometry, validating designs, and analyzing manufacturability. Every model remains fully editable through familiar sketch and feature-tree workflows, with human-readable KCL as its source of truth.

#### Who can benefit from using Zookeeper?

Anyone from beginners and non-engineers to expert CAD users and enterprise teams can benefit from Zookeeper. It speeds up design by turning plain text requests into editable parametric KCL models for newcomers, while saving time for more experienced users with rapid prototyping, project-aware edits, and repeatable workflows that scale for teams.

### Capabilities & Features

#### Where is Zookeeper in Zoo Design Studio?

Zookeeper is a pane on the right side. Click the sparkles icon in the right control bar to open it. It's context-aware and works with your active project to create or edit designs.

#### What types of CAD models can Zookeeper generate?

Zookeeper can generate a wide range of CAD models, from simple primitives and brackets to mechanical parts, enclosures, mounts, assemblies, and 3D-printable components, all from prompts or images. It can also edit existing models, interpret selected geometry and renders, and update the active project by producing or modifying parametric KCL code.

#### Can Zookeeper model things directly from text prompts?

Yes - Describe what you want and Zookeeper will try to generate the geometry as parametric KCL. If generation fails or needs tweaking, it will suggest prompt refinements or follow-up edits.

#### Can Zookeeper suggest my next steps during modeling?

Yes - Zookeeper analyzes your active project and offers context-aware suggestions (e.g., add fillets, mounting holes, or adjust dimensions) to help you decide the next modeling steps. It can also propose small edits or refinements you can apply immediately. It conducts relevant research, proposes design constraints and parameters, and generates a clear design plan before producing a CAD model.

#### Can Zookeeper interpret selections I make in the project?

Yes - Zookeeper understands and uses your selections in the active project. When you select faces, edges, bodies, or code regions, Zookeeper uses that context to make targeted edits, add features, or generate more precise prompts.

#### Can Zookeeper view and interpret renders of my model?

Yes - Zookeeper can view and interpret the project's renders and multiview snapshots to understand geometry and suggest or make context-aware edits. It uses those visual cues alongside selections and KCL to produce more accurate modifications. The team added engine-level tools that allow the agent to inspect, snapshot, and debug geometry while generating production-ready CAD.

#### Can you ask Zookeeper questions?

Yes - You can ask Zookeeper questions about modeling, KCL, design decisions, or your active project. It can research using the internet, explain tradeoffs, and make manufacturing-aware suggestions. When you ask, Zookeeper can also perform edits, apply changes, or generate models directly in your design. The Enterprise version of Zookeeper can also be asked questions relevant to your design rules and internal company knowledge.

#### Can Zookeeper calculate surface area, volume, mass, or center of mass?

Yes. Zookeeper can derive surface area, volume, and center of mass from the geometry in the active project and return results in common units (for example, mm³ or m²). To calculate mass, you must provide the material density and its units; Zookeeper does not automatically infer density from project metadata.

#### How does a user get the most value from Zookeeper?

Be specific about what you want (dimensions, constraints, intended use) and include selections or reference geometry in the active project - clear prompts produce more accurate KCL results. Iterate: review the generated model, tweak parameters or ask for targeted edits, and accept Zookeeper's suggestions (fillets, holes, thickness changes) to quickly refine the design.

#### What languages does Zookeeper understand?

Zookeeper understands natural-language prompts (primarily English) and can read and work with KCL code and selected geometry in your project. It also accepts many major languages (Spanish, French, German, Chinese, etc.) with varying accuracy, though the best results are typically in English.

#### What is Auto Mode in Zookeeper?

Auto Mode helps Zookeeper choose the right model for your prompt automatically.

If you're on the Free Plan, you won't need to pick between Standard and Thoughtful mode. Instead, Zookeeper will use Auto Mode to select the model that makes the most sense for what you're asking. Some prompts need deeper reasoning, while others can be answered just as well with a faster, lighter model.

This helps free users get more out of their included reasoning time by avoiding unnecessary use of more expensive reasoning when it isn't needed. Fancy when it matters, efficient when it doesn't.

Users on paid plans can choose between Standard and Thoughtful mode themselves.

### Code (KCL) & CAD Knowledge

#### What is KCL and how does it relate to Zookeeper?

KCL (KittyCAD Language) is Zoo Design Studio's domain-specific, parametric CAD programming language. KCL projects are collections of .kcl files (entrypoint: main.kcl) that programmatically create 3D geometry using primitives, sketches, transforms, booleans, and parameters.

Zookeeper is our built-in CAD design assistant inside Zoo Design Studio that helps you work with KCL: it can generate new KCL models from plain-language prompts, edit your existing .kcl code, answer questions about KCL, and propose design changes, acting as an intelligent, context-aware partner while you design.

#### Can Zookeeper answer questions about KCL syntax and structure?

Yes - Zookeeper can read your KCL code, explain syntax and structure, and help fix or improve scripts. It can also suggest idiomatic KCL patterns and make project-aware edits when you ask.

#### Can Zookeeper read and understand my KCL code?

Yes - Zookeeper can read and understand your KCL code, explain what it does, and use that context to suggest fixes or make targeted edits to the active project.

#### Does Zookeeper reference official KCL materials?

Yes - Zookeeper references official KCL materials (including the KCL Book) to ensure advice and code follow best practices. See the [KCL Book](https://zoo.dev/docs/kcl-book/intro.html) for details.

#### Can Zookeeper fix KCL bugs?

Yes - Zookeeper can identify and fix KCL errors by analyzing your project and selected code, then applying targeted edits. If an automatic fix can't be applied, it will explain the issue and suggest a clear repair or simplified prompt for you to approve.

#### Can Zookeeper help with mechanical engineering and design concepts?

Yes - Zookeeper can explain mechanical design concepts, recommend best practices (tolerances, fastening, draft, fillets), and help apply them to your model. It can provide guidance and simple calculations, but it doesn't replace engineering validation or guarantee manufacturability or structural performance.

### Limitations

#### What are Zookeeper's limits?

- Can: create and edit KCL CAD models, explain KCL and design concepts, inspect rendered snapshots, analyze geometry, and generate downloadable STEP or STL exports.

- Cannot: run physical tests, guarantee manufacturability or structural safety, or perform detailed engineering simulations.

- Interaction rules: works on the active project through Zoo Design Studio's built-in tools and can return rendered snapshots and generated export files in chat.

- Knowledge bounds: limited to its training and available docs; ask for clarification when requests are vague.

#### What can't Zookeeper do yet?

- Change Zoo Design Studio application settings.

- Directly manipulate your interactive viewport; you still rotate, pan, and zoom it manually. Zookeeper can render separate snapshots from requested camera views for inspection.

- Open or switch to other projects.

- Read files outside the active project directory.

- Access your Zoo account or personal account information.

### Troubleshooting

#### How long will Zookeeper work on my problem before giving up?

Zookeeper will continue working while it is making progress and has the information and tools it needs. The amount of time and number of attempts vary with the complexity of the task. If it cannot continue, it will explain what is blocking it and may ask for clarification, approval, or a smaller request. Breaking a complex task into specific steps can help it make steady progress.

#### What happens when a Zookeeper prompt fails?

When a prompt fails, Zookeeper may inspect the error and try to correct the problem automatically. If it still cannot complete the request, it will explain what went wrong and suggest a next step, such as clarifying the request, breaking it into smaller steps, or making a manual edit. The number of automatic retries varies by task.

#### Can Zookeeper make mistakes?

Yes. Zookeeper can make mistakes - it may misunderstand intent, produce incorrect geometry, or suggest designs that aren't manufacturable or safe. Always review and validate changes, run your own checks, and give clear, specific instructions or corrections when needed.

#### Does Zookeeper support custom instructions or agent rules?

Yes. Add an `AGENTS.md` file to a project to give Zookeeper persistent project-level instructions, constraints, or KCL conventions. Zookeeper reads those rules while working in that project. You can also provide one-time instructions in an individual prompt. Project instructions are separate from global, account-wide personality settings, which are not currently supported.

#### What should I do if Zookeeper struggles to create a full model from a single prompt?

Break the task into smaller steps. Ask Zookeeper for a design plan first, then request geometry changes one feature at a time. Example flow:

1) "Create the rectangular base."

2) "Add corner holes."

3) "Fillet the edges."

Working incrementally (and giving clear dimensions or constraints) gets better results than one large, vague prompt.

#### How do I help Zookeeper focus on the right part of my model?

Select the exact geometry and give a concise instruction.

- In the UI, highlight the face/edge/body or select the relevant lines in the code before asking.

- Use clear, specific commands (e.g., "change this hole diameter to 5 mm" or "fillet these two edges with 2 mm").

- Reference named parts or parameters if available (e.g., "modify mount_plate.thickness").

- Provide constraints or intent when helpful (fit a M4 screw, keep wall ≥2 mm).

Doing this ensures Zookeeper applies changes to the correct part rather than guessing.

#### Where should I report bugs or request features?

You can report bugs in several ways.

1) [Submit a GitHub issue](https://github.com/KittyCAD/modeling-app/)

2) Report bugs on our [Discord server](https://discord.gg/Bee65eqawJ)

3) Ask our team via our [Community Forum](https://community.zoo.dev/)

### API

#### Can I use Zookeeper as an API?

Yes! Zookeeper is built on the [Agent API](/docs/developer-tools/agent-api), and will call any Zoo tool necessary to get the job done. It supports uploading images, documents, 3D models and text as sources to work from.

### Pricing

#### How much does Zookeeper cost?

Zookeeper usage is included with Zoo Design Studio plans as monthly reasoning time.

- Free plans include {{pricing.free.included_usage_minutes}} per month

- Plus plans include {{pricing.plus.included_usage_minutes}} per month

- The Pro plan {{pricing.pro.zookeeper_access}}

If you use up the reasoning time included in your plan, usage pauses by default. You can enable pay-as-you-go at {{pricing.standard.payg_rate}} or upgrade to a higher plan.

## Design Studio Pricing

### Pricing, Billing, Payment

#### What's included in the Free Plan, and how do I know when to upgrade?

The Free plan {{pricing.free.design_studio_access}}. It includes {{pricing.free.included_usage_minutes}} of Zookeeper reasoning time per month when the included usage is spent entirely in Zookeeper. The same {{pricing.free.monthly_included_usage}} of included usage can instead be spent on direct API or Zoo MCP activity. The Free plan {{pricing.free.training_policy}}.

We'll notify you when you're close to or have used up your included usage. You can upgrade at any time from your account settings. If you run out, billable usage pauses by default. You can enable pay-as-you-go at {{pricing.standard.payg_rate}} or upgrade to a higher plan with more included usage.

#### When does my included usage renew, and does unused usage roll over?

Included monthly usage normally refreshes at your account's monthly anniversary boundary, evaluated in UTC. Legacy accounts that still use calendar-month billing periods refresh on the first day of each month at 00:00 UTC instead. This usage refresh is separate from your subscription charge or renewal date, and it remains monthly whether you pay for your subscription monthly or annually. New accounts receive the usage included with their current plan when the account is created. When a refresh date applies to your account, you can see the exact next refresh time on your [Billing page](/account/billing).

The refresh replaces your remaining monthly included-usage balance with the full monthly amount included in your current plan, so unused monthly usage does not roll over or accumulate. Changing plans can also update your available allowance immediately.

Promotional or other usage granted separately by Zoo is not replaced during the monthly refresh. Usage draws from the monthly plan allowance first, then from separately granted usage. You can see your combined remaining balance on your [Billing page](/account/billing).

After all available usage is exhausted, billable usage pauses by default. You can continue on a pay-as-you-go basis if you enable it and have a valid payment method, or upgrade to a plan with more included usage. Otherwise, usage remains paused until the next monthly refresh.

#### What is pay-as-you-go, and is it enabled by default?

Pay-as-you-go lets you continue using billable Zoo services after you have exhausted the usage included with your Free or paid plan, as well as any usage granted separately. Additional usage is charged at the applicable pay-as-you-go rate.

The setting is off by default. While off, billable usage pauses after your available usage is exhausted, so you will not incur overage charges. You can turn pay-as-you-go on or off from your [Billing page](/account/billing). A valid payment method is required before pay-as-you-go charges can be incurred.

#### Why do I now need to opt in to pay-as-you-go?

Zoo now requires explicit consent before usage can continue beyond your available included usage and generate overage charges. Previously, eligible accounts could continue on a pay-as-you-go basis without enabling a separate setting.

Requiring an explicit opt-in gives you direct control over whether your usage should stop at your plan's limit or continue as paid overage usage. You can review or change your choice at any time from your [Billing page](/account/billing).

#### What happens if I turn pay-as-you-go off?

Turning pay-as-you-go off does not affect the usage already included with your plan. You can continue using Zoo until all included and separately granted usage has been exhausted.

After that usage is exhausted, billable usage pauses instead of generating additional charges. Usage can resume when your monthly allowance refreshes, when you receive additional usage, when you upgrade to a plan with more included usage, or when you turn pay-as-you-go back on. Turning it off does not reverse charges for usage that has already occurred.

#### How does pay-as-you-go work on the Pro plan?

The Pro plan {{pricing.pro.zookeeper_access}}. API usage outside Zoo Design Studio is separate: it uses any included API usage available on your account first, then continues at pay-as-you-go rates only if you have enabled pay-as-you-go and have a valid payment method.

#### Does unlimited Zoo Design Studio usage include Zoo MCP or direct API usage?

No. Unlimited use applies to eligible activity inside Zoo Design Studio. Zoo MCP connects an external AI client to Zoo through your API token, so its hosted Zoo operations are treated as API usage outside Zoo Design Studio.

An MCP tool can run locally or make one or more Zoo API calls, so an MCP tool call is not itself the billing unit. Billable API requests use any available included usage first and then pay-as-you-go if it is enabled. See the [API pricing FAQ](/docs/faq#faq-api-pricing) and [API pricing](/api-pricing) for details.

#### Do you offer monthly and annual payment options, and are there discounts for yearly plans?

Available billing intervals and annual savings vary by plan. Use the monthly and annual controls on the [pricing page](/zoo-pricing) to see the current options and prices returned for each plan.

#### What happens when I cancel a paid subscription?

Canceling does not schedule your subscription to end on its next renewal date. It downgrades your account to the Free plan immediately, whether your subscription is billed monthly or annually. Any unused paid time in your current billing period is prorated automatically.

Your Zoo account and data are not deleted, but your paid-plan benefits end immediately. After cancellation, your access is limited to what the Free plan includes; currently, the Free plan {{pricing.free.design_studio_access}}. You can upgrade again at any time.

If you want to avoid the next renewal while keeping paid access through the remainder of your current billing period, the current cancellation flow does not provide that option. Review your subscription and billing dates on your [Billing page](/account/billing) before canceling.

#### Which payment methods are accepted, and can they be changed later?

We accept credit cards for all paid plans. For Team or Enterprise plans, if you need custom billing, please [contact us](/contact).

#### Can I switch between plans anytime without losing data?

Yes, you can always upgrade or downgrade your plan to another tier without losing your data.

### Support & Usage

#### What onboarding resources or training do you provide for new users?

Visit our [Getting Started](/docs/zoo-design-studio/getting-started) documentation and [YouTube channel](https://www.youtube.com/@zoodotdev) for the latest onboarding resources.

#### Are there usage caps on the Free Plan, and how do overages work?

The Free plan includes {{pricing.free.included_usage_minutes}} of Zookeeper reasoning time per month when its {{pricing.free.monthly_included_usage}} of included usage is spent entirely in Zookeeper. The same included usage can instead be spent on direct API or Zoo MCP activity. If you use all of it, you can continue on a pay-as-you-go basis if it is enabled and you have a payment method, upgrade to a plan with more included usage, or wait for the next monthly refresh. Usage normally refreshes at your account's monthly anniversary boundary (UTC); legacy accounts that still use calendar-month billing periods refresh on the first day of each month at 00:00 UTC instead. Check your [Billing page](/account/billing) for your next refresh time. Plans with unlimited Zookeeper usage in Zoo Design Studio are identified on the [pricing page](/zoo-pricing).

### Enterprise

#### Where can I learn about Enterprise plans and capabilities?

Visit the [Zoo Enterprise FAQs](/enterprise#faq-plans-pilots) for information about custom pricing, pilots, model customization, security, deployment, and integrations.

## API Pricing

### Pricing

#### How much do API calls cost?

API calls are charged by the second at {{pricing.standard.payg_rate}}.

Rounding: For each completed call, we round its duration up to the next whole second, multiply by the per-second rate, then round the monetary result to the nearest cent.

Short calls policy: Historically, sub-10-second calls were not billed. Since October 14, 2025, they have been billed per second with the same rate and rounding.

Note: because we round each call to cents, many tiny calls can sum to a hair more than one long call with the same total seconds. This is standard for usage billing. If that ever meaningfully impacts you, tell us.

For more information on how the math works, see Jess's blog post [here](https://zoo.dev/blog/per-second-billing).

#### How much API usage is included?

Included monthly API usage varies by plan. Check the current allowance on the [Zoo Design Studio pricing page](/zoo-pricing) or your [Billing page](/account/billing). Billable activity draws from available included usage first; after it is exhausted, API usage pauses unless pay-as-you-go is enabled and the account has a valid payment method.

#### How is Zoo MCP usage billed?

Zoo MCP does not have a separate subscription or flat per-tool-call fee. Tools that call Zoo's hosted services use your Zoo API token and are billed as API usage outside Zoo Design Studio. Unlimited Zoo Design Studio usage does not make Zoo MCP usage unlimited.

An MCP tool can make no API calls, one API call, or multiple API calls. Billing is based on the underlying successful, billable API requests and persistent API sessions, not the number of MCP tool calls. Available included usage is applied first, followed by pay-as-you-go only when it is enabled. Your AI client, such as Claude or Codex, may charge separately.

See your [Billing page](/account/billing) for your available usage and pay-as-you-go settings.

#### Do all API calls cost the same?

Charged API calls are billed by the second at {{pricing.standard.payg_rate}}. For more information on how the math works, see Jess's blog post [here](https://zoo.dev/blog/per-second-billing).

#### Am I charged for failed API calls?

No, you are not charged if the API call fails.

#### Am I charged for GET API calls?

Generally no. GET requests are free, except for WebSocket-style GETs used for real-time features: endpoints that start with `/ws/modeling/commands` or `/ws/ml/copilot` are billable.

#### Which endpoints are billed?

In general, successful `POST` requests are billable, with some exclusions. The only `GET` endpoints that are billable are WebSocket-style GETs for real-time features: endpoints that start with `/ws/modeling/commands` or `/ws/ml/copilot`.

See the [API Reference](/docs/developer-tools/api) for the current list of available endpoints. To review the API calls charged to your account, visit [Developer settings](/account/developer).

#### Are endpoints that start with /user or /org billed?

No. Endpoints that start with `/user` or `/org` are free and not billed.

#### Are /oauth2 endpoints billed?

No. Endpoints that start with `/oauth2` are free and not billed.

#### Which endpoints are never billed?

The following endpoints, endpoint prefixes, and patterns are free and never billed:
- `/_meta`
- `/user`
- `/logout`
- `/apps`
- `/events`
- `/org`
- `/ml/custom`
- `/store`
- `/_internal`
- `/auth`
- `/oauth2`
- `/debug`
- Any endpoint containing `shortlinks`
- `/file/execute/`
- `/projects/public/{id}/vote`
- `/ws/ml/reasoning/{id}`

### Agent API

#### How long do Agent API calls take?

Agent API requests do not have a fixed completion time. Duration depends on the complexity of the task, the tools required, and the number of iterations the agent performs. Integrations should not assume a specific completion window.

#### The result from the Agent API wasn't great; am I still charged?

Yes. We are working on our machine learning endpoints every day, but it is still experimental. Some results may not be as good as you expect.

#### What file format does the Agent API output?

The Agent API streams conversational responses and tool results. For CAD-generation tasks, those results can include editable KCL project files. Producing formats such as STEP requires a separate modeling and export step.

### Support

#### Where can I get help with using Zoo APIs?

For assistance with APIs, you can ask a question on our [Community Page](https://community.zoo.dev/) or discuss on [our Discord](https://discord.gg/JQEpHR7Nt2)!

#### I think I found a bug, where can I report it?

For bugs, mention it to us on our [Community Page](https://community.zoo.dev/).

#### We need help deploying a large scale API service using Zoo APIs within our company. Who is the best person to contact?

Please [email us](mailto:sales@zoo.dev) directly. We would love to chat with your specific needs and see how we can best help you.

You can also find answers in the [Community Forum](https://community.zoo.com), contact support, or join the Zoo Discord server.
