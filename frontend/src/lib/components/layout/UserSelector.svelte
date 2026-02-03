<script lang="ts">
	import { users, selectedUserId } from '$lib/stores/user';
	import { generatePixelAvatar } from '$lib/utils/pixelAvatar';

	function handleChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		const val = target.value;
		$selectedUserId = val ? Number(val) : null;
	}

	let avatarSvg = $derived($selectedUserId ? generatePixelAvatar($selectedUserId, 24) : '');
</script>

<div class="flex items-center gap-2">
	{#if $selectedUserId}
		<div class="w-6 h-6 border-2 border-[#5a3a1a] dark:border-crt-green shrink-0">
			{@html avatarSvg}
		</div>
	{/if}
	<select
		value={$selectedUserId ?? ''}
		onchange={handleChange}
		class="pixel-input !py-1 !px-2 text-sm max-w-[120px] sm:max-w-none truncate"
	>
		<option value="">-- Held wählen --</option>
		{#each $users as user (user.id)}
			<option value={user.id}>{user.display_name || user.username}</option>
		{/each}
	</select>
</div>
