<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { darkMode } from '$lib/stores/theme';
	import { users } from '$lib/stores/user';
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { createApiClient } from '$lib/api/client';
	import Header from '$lib/components/layout/Header.svelte';
	import Navigation from '$lib/components/layout/Navigation.svelte';
	import Toast from '$lib/components/ui/Toast.svelte';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();

	onMount(() => {
		if ($darkMode) {
			document.documentElement.classList.add('dark');
		}

		if ($apiKey) {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			client.users.list().then((u) => {
				$users = u;
			}).catch(() => {});
		}
	});
</script>

<div class="min-h-screen flex flex-col" class:crt-scanlines={$darkMode}>
	<Header />
	<div class="flex flex-1">
		<Navigation />
		<main class="flex-1 pb-20 md:pb-4">
			<div class="max-w-5xl mx-auto p-4">
				{@render children()}
			</div>
		</main>
	</div>
	<Toast />
</div>
