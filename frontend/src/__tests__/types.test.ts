// TSS PPM v3.0 - Type Tests
import { describe, it, expect } from 'vitest'
import { GoalType, type Goal, type GoalCreate, type GoalUpdate } from '../types'
import { ReviewStage, ReviewStatus, type Review } from '../types'

describe('GoalType enum', () => {
  it('should have correct values', () => {
    expect(GoalType.STANDARD).toBe('STANDARD')
    expect(GoalType.KAR).toBe('KAR')
    expect(GoalType.SCF).toBe('SCF')
  })

  it('should have exactly 3 values', () => {
    const values = Object.values(GoalType)
    expect(values).toHaveLength(3)
  })
})

describe('Goal interface', () => {
  it('should accept valid goal data', () => {
    const goal: Goal = {
      id: '123',
      review_id: '456',
      title: 'Test Goal',
      description: 'Description',
      goal_type: GoalType.STANDARD,
      weight: 25,
      score: 2,
      display_order: 0,
    }

    expect(goal.id).toBe('123')
    expect(goal.title).toBe('Test Goal')
    expect(goal.goal_type).toBe(GoalType.STANDARD)
    expect(goal.weight).toBe(25)
  })

  it('should allow null description and score', () => {
    const goal: Goal = {
      id: '123',
      review_id: '456',
      title: 'Test Goal',
      description: null,
      goal_type: GoalType.KAR,
      weight: 30,
      score: null,
      display_order: 1,
    }

    expect(goal.description).toBeNull()
    expect(goal.score).toBeNull()
  })
})

describe('GoalCreate interface', () => {
  it('should accept minimal required fields', () => {
    const create: GoalCreate = {
      title: 'New Goal',
      weight: 20,
    }

    expect(create.title).toBe('New Goal')
    expect(create.weight).toBe(20)
    expect(create.goal_type).toBeUndefined()
  })

  it('should accept all optional fields', () => {
    const create: GoalCreate = {
      title: 'New Goal',
      description: 'Description',
      goal_type: GoalType.SCF,
      weight: 50,
    }

    expect(create.description).toBe('Description')
    expect(create.goal_type).toBe(GoalType.SCF)
  })
})

describe('GoalUpdate interface', () => {
  it('should allow partial updates', () => {
    const update: GoalUpdate = {
      title: 'Updated Title',
    }

    expect(update.title).toBe('Updated Title')
    expect(update.weight).toBeUndefined()
  })

  it('should allow updating all fields', () => {
    const update: GoalUpdate = {
      title: 'Updated',
      description: 'New description',
      goal_type: GoalType.KAR,
      weight: 35,
    }

    expect(update.title).toBe('Updated')
    expect(update.weight).toBe(35)
  })
})

describe('ReviewStage enum', () => {
  it('should have correct values', () => {
    expect(ReviewStage.GOAL_SETTING).toBe('GOAL_SETTING')
    expect(ReviewStage.MID_YEAR_REVIEW).toBe('MID_YEAR_REVIEW')
    expect(ReviewStage.END_YEAR_REVIEW).toBe('END_YEAR_REVIEW')
  })
})

describe('ReviewStatus enum', () => {
  it('should have all status values', () => {
    expect(ReviewStatus.DRAFT).toBe('DRAFT')
    expect(ReviewStatus.PENDING_EMPLOYEE_SIGNATURE).toBe('PENDING_EMPLOYEE_SIGNATURE')
    expect(ReviewStatus.EMPLOYEE_SIGNED).toBe('EMPLOYEE_SIGNED')
    expect(ReviewStatus.PENDING_MANAGER_SIGNATURE).toBe('PENDING_MANAGER_SIGNATURE')
    expect(ReviewStatus.MANAGER_SIGNED).toBe('MANAGER_SIGNED')
    expect(ReviewStatus.SIGNED).toBe('SIGNED')
    expect(ReviewStatus.ARCHIVED).toBe('ARCHIVED')
  })
})

describe('Review interface', () => {
  it('should accept valid review data', () => {
    const review: Review = {
      id: 'review-1',
      employee_id: 'emp-1',
      manager_id: 'mgr-1',
      status: ReviewStatus.DRAFT,
      stage: ReviewStage.GOAL_SETTING,
      review_year: 2026,
      what_score: null,
      how_score: null,
    }

    expect(review.id).toBe('review-1')
    expect(review.status).toBe(ReviewStatus.DRAFT)
    expect(review.review_year).toBe(2026)
  })
})
