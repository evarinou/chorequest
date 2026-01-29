<script lang="ts">
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { darkMode } from '$lib/stores/theme';
	import { createApiClient, ApiError } from '$lib/api/client';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import { mdiCheck, mdiAlertCircle, mdiWeatherNight, mdiWeatherSunny } from '@mdi/js';

	let testStatus = $state<'idle' | 'loading' | 'success' | 'error'>('idle');
	let testMessage = $state('');

	async function testConnection() {
		testStatus = 'loading';
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const health = await client.health.check();
			testStatus = 'success';
			testMessage = `Verbunden mit ${health.app} v${health.version}`;
		} catch (e) {
			testStatus = 'error';
			testMessage = e instanceof ApiError ? e.detail : 'Verbindung fehlgeschlagen';
		}
	}
</script>

<svelte:head>
	<title>Einstellungen - ChoreQuest</title>
</svelte:head>

<h1 class="text-2xl font-bold mb-6">Einstellungen</h1>

<div class="space-y-6">
	<Card>
		<h2 class="text-lg font-semibold mb-4">API-Verbindung</h2>
		<div class="space-y-4">
			<div>
				<label for="api-url" class="block text-sm font-medium mb-1">API Base URL</label>
				<input
					id="api-url"
					type="url"
					bind:value={$apiBaseUrl}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
					placeholder="http://localhost:8000"
				/>
			</div>
			<div>
				<label for="api-key" class="block text-sm font-medium mb-1">API Key</label>
				<input
					id="api-key"
					type="password"
					bind:value={$apiKey}
					class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
					placeholder="API-Schlüssel eingeben..."
				/>
			</div>
			<div class="flex items-center gap-3">
				<Button onclick={testConnection} disabled={testStatus === 'loading'}>
					{testStatus === 'loading' ? 'Teste...' : 'Verbindung testen'}
				</Button>
				{#if testStatus === 'success'}
					<span class="flex items-center gap-1 text-sm text-success-600 dark:text-success-500">
						<Icon path={mdiCheck} size={16} />
						{testMessage}
					</span>
				{:else if testStatus === 'error'}
					<span class="flex items-center gap-1 text-sm text-danger-500">
						<Icon path={mdiAlertCircle} size={16} />
						{testMessage}
					</span>
				{/if}
			</div>
		</div>
	</Card>

	<Card>
		<h2 class="text-lg font-semibold mb-4">Darstellung</h2>
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<Icon path={$darkMode ? mdiWeatherNight : mdiWeatherSunny} size={20} />
				<span class="text-sm font-medium">
					{$darkMode ? 'Dunkler Modus' : 'Heller Modus'}
				</span>
			</div>
			<button
				onclick={() => { $darkMode = !$darkMode; }}
				aria-label="Dark Mode umschalten"
				class="relative w-12 h-6 rounded-full transition-colors {$darkMode ? 'bg-primary-600' : 'bg-gray-300'}"
			>
				<span
					class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform {$darkMode ? 'translate-x-6' : ''}"
				></span>
			</button>
		</div>
	</Card>
</div>
