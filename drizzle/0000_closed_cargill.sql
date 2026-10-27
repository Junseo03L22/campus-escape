CREATE TABLE `rank_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`player` text NOT NULL,
	`stage` integer NOT NULL,
	`seed` integer NOT NULL,
	`rules` text NOT NULL,
	`started` integer NOT NULL,
	`used` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `rank_runs_player_time` ON `rank_runs` (`player`,`started`);--> statement-breakpoint
CREATE INDEX `rank_runs_expiry` ON `rank_runs` (`started`);--> statement-breakpoint
CREATE TABLE `stage_scores` (
	`player` text NOT NULL,
	`stage` integer NOT NULL,
	`rules` text NOT NULL,
	`nickname` text NOT NULL,
	`score` integer NOT NULL,
	`remaining` integer NOT NULL,
	`created` integer NOT NULL,
	PRIMARY KEY(`player`, `stage`, `rules`)
);
--> statement-breakpoint
CREATE INDEX `stage_scores_ranking` ON `stage_scores` (`rules`,`stage`,`score`,`created`);