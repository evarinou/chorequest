export interface LevelInfo {
	level: number;
	title: string;
	currentXP: number;
	requiredXP: number;
	totalForLevel: number;
	progress: number;
}

const XP_THRESHOLDS = [
	0,      // Level 1: 0
	100,    // Level 2: 100
	300,    // Level 3: 300
	600,    // Level 4: 600
	1000,   // Level 5: 1000
	1500,   // Level 6: 1500
	2200,   // Level 7: 2200
	3000,   // Level 8: 3000
	4000,   // Level 9: 4000
	5200,   // Level 10: 5200
	6600,   // Level 11: 6600
	8200,   // Level 12: 8200
	10000,  // Level 13: 10000
	12000,  // Level 14: 12000
	14500,  // Level 15: 14500
	17500,  // Level 16: 17500
	21000,  // Level 17: 21000
	25000,  // Level 18: 25000
	30000,  // Level 19: 30000
	36000,  // Level 20: 36000
];

const TITLES = [
	'Putz-Lehrling',
	'Wisch-Novize',
	'Staub-Knecht',
	'Haushalts-Knappe',
	'Ordnungs-Geselle',
	'Besen-Krieger',
	'Ordnungs-Ritter',
	'Hygiene-Paladin',
	'Hygiene-Meister',
	'Staub-Magier',
	'Glanz-Beschwörer',
	'Reinigungs-Guru',
	'Putz-Erzmagier',
	'Ordnungs-Champion',
	'Reinigungs-Legende',
	'Hygiene-Halbgott',
	'Staub-Vernichter',
	'Haushalt-Titan',
	'Haushalt-Gott',
	'Putz-Legende',
];

export function getLevelInfo(totalPoints: number): LevelInfo {
	let level = 1;

	for (let i = XP_THRESHOLDS.length - 1; i >= 0; i--) {
		if (totalPoints >= XP_THRESHOLDS[i]) {
			level = i + 1;
			break;
		}
	}

	const currentThreshold = XP_THRESHOLDS[level - 1] ?? 0;
	const nextThreshold = XP_THRESHOLDS[level] ?? currentThreshold + 5000;

	const currentXP = totalPoints - currentThreshold;
	const requiredXP = nextThreshold - currentThreshold;
	const progress = Math.min(100, (currentXP / requiredXP) * 100);

	const title = TITLES[Math.min(level - 1, TITLES.length - 1)];

	return {
		level,
		title,
		currentXP,
		requiredXP,
		totalForLevel: currentThreshold,
		progress
	};
}
