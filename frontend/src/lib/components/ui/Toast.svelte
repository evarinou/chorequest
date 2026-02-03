<script lang="ts">
	import { toasts } from '$lib/stores/toast';
	import { mdiCheck, mdiAlertCircle, mdiInformation, mdiStar, mdiTrophy } from '@mdi/js';
	import Icon from './Icon.svelte';

	const iconMap: Record<string, string> = {
		success: mdiCheck,
		error: mdiAlertCircle,
		info: mdiInformation,
		points: mdiStar,
		achievement: mdiTrophy
	};

	const prefixMap: Record<string, string> = {
		success: 'QUEST COMPLETE!',
		error: 'FEHLER!',
		info: 'INFO',
		points: 'XP ERHALTEN!',
		achievement: 'ACHIEVEMENT!'
	};

	const colorMap: Record<string, string> = {
		success: 'border-nes-green bg-nes-green/10 text-nes-green',
		error: 'border-nes-red bg-nes-red/10 text-nes-red',
		info: 'border-nes-blue bg-nes-blue/10 text-nes-blue',
		points: 'border-nes-gold bg-nes-gold/10 text-nes-gold',
		achievement: 'border-nes-purple bg-nes-purple/10 text-nes-purple'
	};

	const darkColorMap: Record<string, string> = {
		success: 'dark:border-crt-green dark:bg-crt-panel dark:text-crt-green',
		error: 'dark:border-nes-red dark:bg-crt-panel dark:text-nes-red',
		info: 'dark:border-crt-green dark:bg-crt-panel dark:text-crt-green',
		points: 'dark:border-nes-gold dark:bg-crt-panel dark:text-nes-gold',
		achievement: 'dark:border-nes-purple dark:bg-crt-panel dark:text-nes-purple'
	};
</script>

<div class="fixed bottom-20 md:bottom-4 right-4 z-50 flex flex-col gap-2 max-w-[calc(100vw-2rem)] sm:max-w-sm">
	{#each $toasts as toast (toast.id)}
		<div class="animate-pixel-slide-in border-3 px-4 py-3 {colorMap[toast.type]} {darkColorMap[toast.type]}">
			<div class="flex items-center gap-3">
				<Icon path={iconMap[toast.type]} size={18} />
				<div>
					<div class="text-[8px] font-bold mb-1" style="font-family: 'Press Start 2P', monospace;">
						{prefixMap[toast.type]}
					</div>
					<span class="text-sm">{toast.message}</span>
				</div>
			</div>
		</div>
	{/each}
</div>
