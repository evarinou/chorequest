<script lang="ts">
	import type { TaskInstanceWithDetails } from '$lib/api/types';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { mdiCheck, mdiClock, mdiStar } from '@mdi/js';

	interface Props {
		instance: TaskInstanceWithDetails;
		oncomplete: (instance: TaskInstanceWithDetails) => void;
	}

	let { instance, oncomplete }: Props = $props();

	let today = $derived(new Date().toLocaleDateString('sv-SE'));
	let isCompleted = $derived(instance.status === 'completed');
	let isSkipped = $derived(instance.status === 'skipped');
	let isOverdue = $derived(instance.status === 'pending' && !!instance.due_date && instance.due_date < today);
	let isHighValue = $derived(instance.task.base_points >= 15);

	let difficultyStars = $derived(
		instance.task.base_points >= 20 ? '★★★' :
		instance.task.base_points >= 10 ? '★★' :
		'★'
	);

	let formattedDueDate = $derived.by(() => {
		if (!isOverdue) return '';
		const [, m, d] = instance.due_date.split('-');
		return `${d}.${m}.`;
	});
</script>

<div
	class="flex items-center gap-3 p-3 pixel-border bg-parchment-50 dark:bg-crt-panel transition-colors {isCompleted || isSkipped ? 'opacity-50' : 'hover:bg-parchment-200 dark:hover:bg-crt-dark-green cursor-pointer'} {isHighValue && !isCompleted && !isSkipped && !isOverdue ? 'border-nes-gold!' : ''} {isOverdue ? 'border-l-4 border-l-nes-red' : ''}"
>
	{#if isCompleted}
		<div class="shrink-0 text-nes-green dark:text-crt-green text-xl">✓</div>
	{:else if isSkipped}
		<div class="shrink-0 text-parchment-400 dark:text-crt-green/40 text-xl">—</div>
	{:else}
		<div class="shrink-0 text-nes-gold text-sm">{difficultyStars}</div>
	{/if}

	<div class="flex-1 min-w-0">
		<div class="flex items-center gap-2">
			<span class="text-sm truncate {isCompleted ? 'line-through' : ''}">
				{instance.task.title}
			</span>
			{#if isOverdue}
				<Badge variant="danger">VERPASST</Badge>
			{/if}
		</div>
		<div class="flex items-center gap-3 mt-1 text-xs text-parchment-400 dark:text-crt-green/60">
			<Badge variant="points">{instance.task.base_points} XP</Badge>
			{#if isOverdue}
				<span class="text-nes-red">Fällig: {formattedDueDate}</span>
			{/if}
			{#if instance.task.estimated_minutes}
				<span class="flex items-center gap-1">
					<Icon path={mdiClock} size={12} />
					{instance.task.estimated_minutes} Min.
				</span>
			{/if}
			{#if instance.assigned_user}
				<Badge>{instance.assigned_user.display_name || instance.assigned_user.username}</Badge>
			{/if}
		</div>
	</div>
	{#if instance.status === 'pending'}
		<Button size="sm" onclick={() => oncomplete(instance)}>
			<Icon path={mdiCheck} size={16} />
			OK!
		</Button>
	{:else if isCompleted}
		<Badge variant="success">DONE</Badge>
	{:else if isSkipped}
		<Badge variant="default">SKIP</Badge>
	{/if}
</div>
