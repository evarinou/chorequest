<script lang="ts">
	import { mdiCog } from '@mdi/js';
	import Icon from '$lib/components/ui/Icon.svelte';
	import UserSelector from './UserSelector.svelte';
</script>

<header class="sticky top-0 z-40 bg-white/80 dark:bg-gray-800/80 backdrop-blur border-b border-gray-200 dark:border-gray-700">
	<div class="max-w-5xl mx-auto flex items-center justify-between px-4 h-14">
		<a href="/" class="flex items-center gap-2 font-bold text-lg text-primary-600 dark:text-primary-400">
			<img src="/logo.svg" alt="ChoreQuest Logo" class="h-8 w-8" />
			ChoreQuest
		</a>
		<div class="flex items-center gap-3">
			<UserSelector />
			<a
				href="/einstellungen"
				class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-400"
			>
				<Icon path={mdiCog} size={20} />
			</a>
		</div>
	</div>
</header>
