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

	let today = new Date().toLocaleDateString('sv-SE');
	let pendingCount = $derived(instances.filter((i) => i.status === 'pending').length);
	let overdueCount = $derived(instances.filter((i) => i.status === 'pending' && i.due_date && i.due_date < today).length);
</script>

<div class="mb-4">
	<button
		onclick={() => { expanded = !expanded; }}
		class="w-full text-left"
	>
		<div class="flex items-center gap-2 py-2">
			<span class="flex-1 h-[2px] bg-parchment-400 dark:bg-crt-green/50"></span>
			<span class="text-[10px] text-parchment-400 dark:text-crt-green shrink-0" style="font-family: 'Press Start 2P', monospace;">
				[ {room.name.toUpperCase()} ]
			</span>
			<span class="flex-1 h-[2px] bg-parchment-400 dark:bg-crt-green/50"></span>
			{#if overdueCount > 0}
				<Badge variant="danger">{overdueCount} VERPASST</Badge>
			{/if}
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
