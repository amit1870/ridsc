
describe "RIDS Open Source", ->
  
  it "should have a rids object at its root", ->
    expect(rids).toBeDefined()

  it "should have an instance of Assets on the rids object", ->
    expect(rids.Assets).toBeDefined()
    expect(rids.Assets).toEqual         jasmine.any(rids.collections.Assets)
    expect(rids.ActiveAssets).toEqual   jasmine.any(rids.collections.ActiveAssets)
    expect(rids.InactiveAssets).toEqual jasmine.any(rids.collections.InactiveAssets)
  
  describe "Models", ->

    it "should exist", ->
      expect(rids.models).toBeDefined()

    describe "Asset model", ->
      it "should exist", ->
        expect(rids.models.Asset).toBeDefined()

  describe "Collections", ->

    it "should exist", ->
      expect(rids.collections).toBeDefined()
    
    describe "Assets", ->
      it "should exist", ->
        expect(rids.collections.Assets).toBeDefined()
        expect(rids.collections.ActiveAssets).toBeDefined()
        expect(rids.collections.InactiveAssets).toBeDefined()

      it "should use the Asset model", ->
        assets = new rids.collections.Assets()
        expect(assets.model).toBe rids.models.Asset

      it "should populate ActiveAssets and InactiveAssets when fetched", ->
        rids.Assets.reset [
            {name: "zacharytamas.com", mimetype:"webpage", is_active: true},
        ]

        # ActiveAssets should have one model now
        expect(rids.ActiveAssets.models.length).toEqual 1

        # InactiveAssets should still be empty
        expect(rids.InactiveAssets.models.length).toEqual 0

        # Now make the page inactive and confirm that ActiveAssets
        # is empty (the previous information is wiped away on a
        # new data load) and the InactiveAssets collection contains
        # the new asset.

        rids.Assets.reset [
            {name: "zacharytamas.com", mimetype:"webpage", is_active: false},
        ]

        # ActiveAssets should be empty now
        expect(rids.ActiveAssets.models.length).toEqual 0

        # InactiveAssets should have a model
        expect(rids.InactiveAssets.models.length).toEqual 1

        rids.Assets.reset [
            {name: "zacharytamas.com", mimetype:"webpage", is_active: false},
            {name: "Hacker News", mimetype: "webpage", is_active: true}
        ]

        # They should both have a model now
        expect(rids.ActiveAssets.models.length).toEqual 1
        expect(rids.InactiveAssets.models.length).toEqual 1
        expect(rids.Assets.models.length).toEqual 2

  describe "Views", ->

    it "should exist", ->
      expect(rids.views).toBeDefined()
