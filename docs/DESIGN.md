# System Design

The agent simulator maps user language to a registered mock tool. It treats retrieved content as untrusted context. The risk engine combines normalized signals: tool sensitivity (32%), permission gap (22%), untrusted source (16%), suspicious sequence (15%), and injection signal (15%). Scores below 35 allow execution; scores from 35 to 69 may require approval; scores of 70 or above block. Hard restrictions override score: unknown tool, missing permission, or detected injection block. Transfers and deletes always require approval after permission validation.

The policy model intentionally separates a score from enforcement. This makes the reasons inspectable and prevents an apparently low weighted score from bypassing a non-negotiable rule.
