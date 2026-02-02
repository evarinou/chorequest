<script lang="ts">
	import { apiBaseUrl, apiKey } from '$lib/stores/config';
	import { darkMode } from '$lib/stores/theme';
	import { createApiClient, ApiError } from '$lib/api/client';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Icon from '$lib/components/ui/Icon.svelte';
	import { mdiCheck, mdiAlertCircle } from '@mdi/js';

	let testStatus = $state<'idle' | 'loading' | 'success' | 'error'>('idle');
	let testMessage = $state('');

	async function testConnection() {
		testStatus = 'loading';
		try {
			const client = createApiClient(fetch, $apiBaseUrl, $apiKey);
			const health = await client.health.check();
			testStatus = 'success';
			testMessage = `Verbunden: ${health.app} v${health.version}`;
		} catch (e) {
			testStatus = 'error';
			testMessage = e instanceof ApiError ? e.detail : 'Verbindung fehlgeschlagen';
		}
	}
</script>

<svelte:head>
	<title>Einstellungen - ChoreQuest</title>
</svelte:head>

<h1 class="text-sm mb-6">OPTIONEN</h1>

<div class="space-y-6">
	<Card>
		<h2 class="text-[10px] mb-4" style="font-family: 'Press Start 2P', monospace;">API-VERBINDUNG</h2>
		<div class="space-y-4">
			<div>
				<label for="api-url" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">BASE URL</label>
				<input
					id="api-url"
					type="url"
					bind:value={$apiBaseUrl}
					class="pixel-input"
					placeholder="http://localhost:8000"
				/>
			</div>
			<div>
				<label for="api-key" class="block text-[9px] mb-1" style="font-family: 'Press Start 2P', monospace;">API KEY</label>
				<input
					id="api-key"
					type="password"
					bind:value={$apiKey}
					class="pixel-input"
					placeholder="API-Schlüssel..."
				/>
			</div>
			<div class="flex items-center gap-3">
				<Button onclick={testConnection} disabled={testStatus === 'loading'}>
					{testStatus === 'loading' ? 'TESTE...' : 'VERBINDUNG TESTEN'}
				</Button>
				{#if testStatus === 'success'}
					<span class="flex items-center gap-1 text-nes-green dark:text-crt-green text-sm">
						<Icon path={mdiCheck} size={16} />
						{testMessage}
					</span>
				{:else if testStatus === 'error'}
					<span class="flex items-center gap-1 text-nes-red text-sm">
						<Icon path={mdiAlertCircle} size={16} />
						{testMessage}
					</span>
				{/if}
			</div>
		</div>
	</Card>

	<Card>
		<h2 class="text-[10px] mb-4" style="font-family: 'Press Start 2P', monospace;">DARSTELLUNG</h2>
		<div class="flex items-center justify-between">
			<span class="text-sm">
				{$darkMode ? '🌙 CRT-Modus (Dunkel)' : '☀️ Pergament-Modus (Hell)'}
			</span>
			<button
				onclick={() => { $darkMode = !$darkMode; }}
				aria-label="Dark Mode umschalten"
				class="pixel-toggle {$darkMode ? 'active' : ''}"
			>
				<span class="pixel-toggle-knob"></span>
			</button>
		</div>
	</Card>
</div>
