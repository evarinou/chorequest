<script lang="ts">
	import type { AchievementProgress } from '$lib/api/types';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import ProgressBar from './ProgressBar.svelte';
	import { mdiTrophy, mdiLock } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';

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

<Card class="{progress.unlocked ? 'gradient-card-gold border-0 relative overflow-hidden' : 'opacity-80 hover:opacity-100 transition-opacity'}">
	{#if progress.unlocked}
		<div class="absolute inset-0 animate-shimmer pointer-events-none"></div>
	{/if}
	<div class="flex items-start gap-3 relative">
		<div class="shrink-0 mt-0.5">
			{#if progress.unlocked}
				<span class="animate-bounce-in inline-block">
					<Icon path={mdiTrophy} size={28} class="text-yellow-600 dark:text-yellow-300" />
				</span>
			{:else}
				<span class="inline-block hover:animate-[bounce-in_0.3s_ease-out] cursor-default">
					<Icon path={mdiLock} size={28} class="text-gray-400" />
				</span>
			{/if}
		</div>
		<div class="flex-1 min-w-0">
			<div class="flex items-center gap-2">
				<span class="font-semibold text-sm">{progress.achievement.name}</span>
				<Badge variant="points">+{progress.achievement.points_reward}</Badge>
			</div>
			{#if progress.achievement.description}
				<p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{progress.achievement.description}</p>
			{/if}
			{#if progress.unlocked && progress.unlocked_at}
				<p class="text-xs text-success-600 dark:text-success-500 mt-2">
					Freigeschaltet am {formatDate(progress.unlocked_at)}
				</p>
			{:else}
				<div class="mt-2">
					<ProgressBar value={progress.progress_percent} />
					<p class="text-xs text-gray-400 mt-1">
						{progress.current_value} / {progress.target_value}
					</p>
				</div>
			{/if}
		</div>
	</div>
</Card>
