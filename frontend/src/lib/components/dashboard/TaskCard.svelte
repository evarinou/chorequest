<script lang="ts">
	import type { TaskInstanceWithDetails } from '$lib/api/types';
	import { mdiCheck, mdiClock, mdiStar } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		instance: TaskInstanceWithDetails;
		oncomplete: (instance: TaskInstanceWithDetails) => void;
	}

	let { instance, oncomplete }: Props = $props();

	let isCompleted = $derived(instance.status === 'completed');
	let isSkipped = $derived(instance.status === 'skipped');
	let isHighValue = $derived(instance.task.base_points >= 15);
</script>

<div
	class="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 transition-all duration-200 {isCompleted || isSkipped ? 'opacity-60' : 'hover:scale-[1.02] hover:shadow-md active:scale-95 cursor-pointer'} {isHighValue && !isCompleted && !isSkipped ? 'border-l-4 border-l-accent-400' : ''}"
>
	<div class="flex-1 min-w-0">
		<div class="flex items-center gap-2">
			<span class="font-medium text-sm truncate {isCompleted ? 'line-through' : ''}">
				{instance.task.title}
			</span>
		</div>
		<div class="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
			<span class="flex items-center gap-1">
				<Icon path={mdiStar} size={12} />
				{instance.task.base_points} Pkt.
			</span>
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
			Erledigt
		</Button>
	{:else if isCompleted}
		<Badge variant="success">Erledigt</Badge>
	{:else if isSkipped}
		<Badge variant="default">Übersprungen</Badge>
	{/if}
</div>
