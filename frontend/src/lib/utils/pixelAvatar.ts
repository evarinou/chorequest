function hashCode(str: string): number {
	let hash = 0;
	for (let i = 0; i < str.length; i++) {
		const char = str.charCodeAt(i);
		hash = ((hash << 5) - hash) + char;
		hash = hash & hash;
	}
	return Math.abs(hash);
}

const AVATAR_COLORS = [
	'#e74040', // NES red
	'#4080e0', // NES blue
	'#40b830', // NES green
	'#f0b028', // NES gold
	'#a040c0', // NES purple
	'#f08020', // NES orange
	'#e05080', // Pink
	'#30b0b0', // Teal
];

export function generatePixelAvatar(identifier: string | number, size: number = 40): string {
	const seed = hashCode(String(identifier));
	const color = AVATAR_COLORS[seed % AVATAR_COLORS.length];
	const pixelSize = size / 5;

	// Generate a 5x5 symmetric grid (only need left half + center)
	const grid: boolean[][] = [];
	for (let y = 0; y < 5; y++) {
		grid[y] = [];
		for (let x = 0; x < 3; x++) {
			grid[y][x] = ((seed >> (y * 3 + x)) & 1) === 1;
		}
		// Mirror
		grid[y][3] = grid[y][1];
		grid[y][4] = grid[y][0];
	}

	// Always fill center column for a more solid look
	for (let y = 0; y < 5; y++) {
		grid[y][2] = true;
	}
	// Always fill some top/bottom for head/feet feel
	grid[0][1] = true;
	grid[0][3] = true;
	grid[4][1] = true;
	grid[4][3] = true;

	let rects = '';
	for (let y = 0; y < 5; y++) {
		for (let x = 0; x < 5; x++) {
			if (grid[y][x]) {
				rects += `<rect x="${x * pixelSize}" y="${y * pixelSize}" width="${pixelSize}" height="${pixelSize}" fill="${color}"/>`;
			}
		}
	}

	return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" shape-rendering="crispEdges" style="image-rendering:pixelated"><rect width="${size}" height="${size}" fill="#1a1a2e"/>${rects}</svg>`;
}

export function pixelAvatarDataUri(identifier: string | number, size: number = 40): string {
	const svg = generatePixelAvatar(identifier, size);
	return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}
