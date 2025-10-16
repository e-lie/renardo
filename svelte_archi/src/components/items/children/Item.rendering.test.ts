// file: src/components/items/children/Item.rendering.test.ts

// import a reference to testing library "render"
import { render, screen, prettyDOM } from '@testing-library/svelte'

// import reference to our interface
import type { ItemInterface } from '@/models'
// import reference to your Item component:
import component from './Item.component.svelte'

describe('Item.component: rendering', () => {
  it('renders an Item text correctly', () => {
    // our data to pass to our component:
    const item: ItemInterface = {
      id: 1,
      name: 'Unit test item 1',
      selected: false
    }

    const testid = 'unit-test-appearance-1'

    // render component
    render(component, {
      testid,
      item // passing the data through the item property
    })

    // get element reference by testid
    const liElement = screen.getByTestId(testid)

    // test
    expect(liElement).not.toBeNull()
    expect(liElement.innerHTML).toContain('Unit test item 1')
  })

  it('has expected css class when selected is true', () => {
    // our data to pass to our component:
    const item: ItemInterface = {
      id: 1,
      name: 'Unit test item 2',
      selected: true // note this is true
    }

    const testid = 'unit-test-appearance-2'

    // render component
    render(component, {
      testid,
      item
    })

    // get element reference by testid
    const liElement = screen.getByTestId(testid)

    // test
    expect(liElement).not.toBeNull()
    // check that the element className attribute has the expected value
    expect(liElement.className).toContain('selected')
  })

  it('has expected css class when selected is false', () => {
    // our data to pass to our component:
    const item: ItemInterface = {
      id: 1,
      name: 'Unit test item 3',
      selected: false // note this is false
    }

    const testid = 'unit-test-appearance-3'

    // render component
    render(component, {
      testid,
      item
    })

    // get element reference by testid
    const liElement = screen.getByTestId(testid)

    // test
    expect(liElement).not.toBeNull()
    // check that the element className attribute has the expected value
    expect(liElement.className).not.toContain('selected')
  })
})
