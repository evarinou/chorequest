<script lang="ts">
	import { slide } from 'svelte/transition';
	import type { Room, TaskInstanceWithDetails } from '$lib/api/types';
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
		class="w-full text-left"
	>
		<div class="flex items-center gap-2 py-2">
			<span class="text-parchment-400 dark:text-crt-green/50">=====</span>
			<span class="text-[10px] text-parchment-400 dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
				[ {room.name.toUpperCase()} ]
			</span>
			<span class="text-parchment-400 dark:text-crt-green/50 flex-1">=====</span>
			{#if pendingCount > 0}
				<Badge variant="points">{pendingCount}</Badge>
			{/if}
			{#if room.point_multiplier !== 1.0}
				<Badge variant="warning">{room.point_multiplier}x</Badge>
			{/if}
			<span class="text-parchment-400 dark:text-crt-green/50 text-sm">
				{expanded ? '▼' : '▶'}
			</span>
		</div>
	</button>

	{#if expanded}
		<div class="space-y-2 pl-2" transition:slide={{ duration: 150 }}>
			{#each instances as instance (instance.id)}
				<TaskCard {instance} {oncomplete} />
			{/each}
		</div>
	{/if}
</div>
