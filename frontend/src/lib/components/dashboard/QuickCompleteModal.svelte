<script lang="ts">
	import type { TaskInstanceWithDetails } from '$lib/api/types';
	import { users, selectedUserId } from '$lib/stores/user';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		open: boolean;
		instance: TaskInstanceWithDetails | null;
		onclose: () => void;
		oncomplete: (instanceId: number, userId: number, notes: string) => void;
	}

	let { open, instance, onclose, oncomplete }: Props = $props();

	let userId = $state<number | null>(null);
	let notes = $state('');
	let submitting = $state(false);

	$effect(() => {
		if (open) {
			userId = $selectedUserId;
			notes = '';
			submitting = false;
		}
	});

	async function handleSubmit() {
		if (!instance || !userId) return;
		submitting = true;
		oncomplete(instance.id, userId, notes);
	}
</script>

<Modal {open} title="QUEST ABSCHLIESSEN" {onclose}>
	{#if instance}
		<div class="space-y-4">
			<div>
				<p class="text-sm" style="font-family: 'Press Start 2P', monospace;">{instance.task.title}</p>
				{#if instance.task.description}
					<p class="text-sm text-parchment-400 dark:text-crt-green/70 mt-1">{instance.task.description}</p>
				{/if}
			</div>

			<div>
				<label for="user-select" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">HELD</label>
				<select
					id="user-select"
					bind:value={userId}
					class="pixel-input"
				>
					<option value={null}>-- Held wählen --</option>
					{#each $users as user (user.id)}
						<option value={user.id}>{user.display_name || user.username}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="notes" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">NOTIZEN</label>
				<textarea
					id="notes"
					bind:value={notes}
					rows={2}
					class="pixel-input"
					placeholder="Optional..."
				></textarea>
			</div>

			<div class="flex gap-3 justify-end">
				<Button variant="secondary" onclick={onclose}>ZURÜCK</Button>
				<Button onclick={handleSubmit} disabled={!userId || submitting}>
					{submitting ? 'SPEICHERT...' : 'ERLEDIGT!'}
				</Button>
			</div>
		</div>
	{/if}
</Modal>
