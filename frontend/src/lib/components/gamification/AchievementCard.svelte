<script lang="ts">
	import type { AchievementProgress } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import ProgressBar from './ProgressBar.svelte';

	interface Props {
		progress: AchievementProgress;
	}

	let { progress }: Props = $props();

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('de-DE', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric'
		});
	}
</script>

<Card class="{progress.unlocked ? 'pixel-border-gold relative overflow-hidden' : 'opacity-70 hover:opacity-100 transition-opacity'}">
	{#if progress.unlocked}
		<div class="absolute inset-0 animate-shimmer pointer-events-none"></div>
	{/if}
	<div class="flex items-start gap-3 relative">
		<div class="shrink-0 mt-0.5 text-2xl">
			{#if progress.unlocked}
				<span class="animate-pixel-pop-in inline-block">🏆</span>
			{:else}
				<span class="grayscale opacity-50">🔒</span>
			{/if}
		</div>
		<div class="flex-1 min-w-0">
			<div class="flex items-center gap-2 flex-wrap">
				<span class="text-[9px]" style="font-family: 'Press Start 2P', monospace;">
					{progress.achievement.name}
				</span>
				<Badge variant="points">+{progress.achievement.points_reward} XP</Badge>
			</div>
			{#if progress.achievement.description}
				<p class="text-sm text-parchment-400 dark:text-crt-green/70 mt-1">{progress.achievement.description}</p>
			{/if}
			{#if progress.unlocked && progress.unlocked_at}
				<p class="text-[8px] text-nes-green dark:text-crt-green mt-2" style="font-family: 'Press Start 2P', monospace;">
					FREIGESCHALTET {formatDate(progress.unlocked_at)}
				</p>
			{:else}
				<div class="mt-2">
					<ProgressBar value={progress.progress_percent} />
					<p class="text-xs text-parchment-400 dark:text-crt-green/50 mt-1">
						{progress.current_value} / {progress.target_value}
					</p>
				</div>
			{/if}
		</div>
	</div>
</Card>
