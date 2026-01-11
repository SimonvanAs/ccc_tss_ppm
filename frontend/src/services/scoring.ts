// TSS PPM v3.0 - Scoring Service with VETO Calculations

export interface GoalScore {
  id: string
  score: number
  weight: number
  goalType: 'STANDARD' | 'KAR' | 'SCF'
}

export interface CompetencyScore {
  id: string
  score: number
}

export interface ScoreResult {
  score: number
  vetoActive: boolean
  vetoReason?: 'SCF' | 'KAR' | 'COMPETENCY'
}

export interface ScfVetoResult {
  active: boolean
  goalId?: string
}

export interface KarVetoResult {
  active: boolean
  goalId?: string
  compensated: boolean
  compensatingGoalId?: string
}

export interface CompetencyVetoResult {
  active: boolean
  competencyId?: string
}

/**
 * Check if SCF VETO is triggered.
 * SCF VETO: If ANY SCF goal scores 1, VETO is active.
 */
export function checkScfVeto(goals: GoalScore[]): ScfVetoResult {
  const scfGoalWith1 = goals.find(g => g.goalType === 'SCF' && g.score === 1)

  if (scfGoalWith1) {
    return { active: true, goalId: scfGoalWith1.id }
  }

  return { active: false }
}

/**
 * Check if KAR VETO is triggered.
 * KAR VETO: If KAR goal scores 1, VETO is active UNLESS compensated by another KAR goal scoring 3.
 * Each KAR=3 can compensate exactly one KAR=1.
 */
export function checkKarVeto(goals: GoalScore[]): KarVetoResult {
  const karGoals = goals.filter(g => g.goalType === 'KAR')
  const karGoalsWith1 = karGoals.filter(g => g.score === 1)
  const karGoalsWith3 = karGoals.filter(g => g.score === 3)

  if (karGoalsWith1.length === 0) {
    return { active: false, compensated: false }
  }

  // Each KAR=3 compensates one KAR=1
  const uncompensatedCount = karGoalsWith1.length - karGoalsWith3.length

  if (uncompensatedCount > 0) {
    // VETO is active - not enough KAR=3 to compensate all KAR=1
    return {
      active: true,
      goalId: karGoalsWith1[0].id,
      compensated: false,
    }
  }

  // All KAR=1 are compensated
  return {
    active: false,
    compensated: true,
    compensatingGoalId: karGoalsWith3[0]?.id,
  }
}

/**
 * Check if Competency VETO is triggered.
 * Competency VETO: If ANY competency scores 1, VETO is active.
 */
export function checkCompetencyVeto(competencies: CompetencyScore[]): CompetencyVetoResult {
  const competencyWith1 = competencies.find(c => c.score === 1)

  if (competencyWith1) {
    return { active: true, competencyId: competencyWith1.id }
  }

  return { active: false }
}

/**
 * Calculate the WHAT score (Goals axis).
 *
 * Formula: Σ(Goal Score × Weight) / 100
 *
 * VETO Rules (in priority order):
 * 1. SCF VETO: If ANY SCF goal = 1 → Score = 1.00
 * 2. KAR VETO: If KAR goal = 1 without compensation → Score = 1.00
 */
export function calculateWhatScore(goals: GoalScore[]): ScoreResult {
  if (goals.length === 0) {
    return { score: 0, vetoActive: false }
  }

  // Check SCF VETO first (highest priority)
  const scfVeto = checkScfVeto(goals)
  if (scfVeto.active) {
    return {
      score: 1,
      vetoActive: true,
      vetoReason: 'SCF',
    }
  }

  // Check KAR VETO
  const karVeto = checkKarVeto(goals)
  if (karVeto.active) {
    return {
      score: 1,
      vetoActive: true,
      vetoReason: 'KAR',
    }
  }

  // No VETO - calculate weighted average
  const totalWeightedScore = goals.reduce((sum, goal) => {
    return sum + (goal.score * goal.weight)
  }, 0)

  const totalWeight = goals.reduce((sum, goal) => sum + goal.weight, 0)
  const score = totalWeight > 0 ? totalWeightedScore / totalWeight : 0

  // Round to 2 decimal places
  const roundedScore = Math.round(score * 100) / 100

  return {
    score: roundedScore,
    vetoActive: false,
  }
}

/**
 * Calculate the HOW score (Competencies axis).
 *
 * Formula: Average of all competency scores
 *
 * VETO Rule:
 * - If ANY competency = 1 → Score = 1.00
 */
export function calculateHowScore(competencies: CompetencyScore[]): ScoreResult {
  if (competencies.length === 0) {
    return { score: 0, vetoActive: false }
  }

  // Check Competency VETO
  const competencyVeto = checkCompetencyVeto(competencies)
  if (competencyVeto.active) {
    return {
      score: 1,
      vetoActive: true,
      vetoReason: 'COMPETENCY',
    }
  }

  // No VETO - calculate simple average
  const totalScore = competencies.reduce((sum, c) => sum + c.score, 0)
  const score = totalScore / competencies.length

  // Round to 2 decimal places
  const roundedScore = Math.round(score * 100) / 100

  return {
    score: roundedScore,
    vetoActive: false,
  }
}
