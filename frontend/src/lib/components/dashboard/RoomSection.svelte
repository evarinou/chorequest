<script lang="ts">
	import { slide } from 'svelte/transition';
	import type { Room, TaskInstanceWithDetails } from '$lib/api/types';
	import { mdiChevronDown, mdiChevronUp } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import TaskCard from './TaskCard.svelte';

	interface Props {
		room: Room;
		instances: TaskInstanceWithDetails[];
		oncomplete: (instance: TaskInstanceWithDetails) => void;
	}

	let { room, instances, oncomplete }: Props = $props();
	let expanded = $state(true);

	let pendingCount = $derived(instances.filter((i) => i.status === 'pending').length);
</script>

<div class="mb-4">
	<button
		onclick={() => { expanded = !expanded; }}
		class="w-full flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750 hover:shadow-md transition-all duration-200"
	>
		<div class="flex items-center gap-3">
			<span class="text-lg font-semibold">{room.name}</span>
			{#if pendingCount > 0}
				<Badge variant="points">{pendingCount} offen</Badge>
			{/if}
			{#if room.point_multiplier !== 1.0}
				<Badge variant="warning">{room.point_multiplier}x</Badge>
			{/if}
		</div>
		<Icon path={expanded ? mdiChevronUp : mdiChevronDown} size={20} class="text-gray-400" />
	</button>

	{#if expanded}
		<div class="mt-2 space-y-2 pl-2" transition:slide={{ duration: 200 }}>
			{#each instances as instance (instance.id)}
				<TaskCard {instance} {oncomplete} />
			{/each}
		</div>
	{/if}
</div>
