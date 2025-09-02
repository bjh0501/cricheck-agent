
class PlaceGraphql:
    def __init__(self):
        self.query = ""
        self.variables = ""

        self.keyword = ""
        self.start = 0
        self.locationX = ""
        self.locationY = ""

    def getPlace(self):
        self.query = '''
            query getPlacesList($input: PlacesInput!) {
                businesses: places(input: $input) {
                    total
                    items {
                        id
                        name
                        normalizedName
                        category
                        x
                        y
                        distance
                    }
                }
            }
            '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "start": self.start,
                "display": 50,
                "x": self.locationX,
                "y": self.locationY,
                "bounds": '500',
                "deviceType": "pcmap"
            }
        }

    def getRestaurant(self):
        self.query = '''
            query getRestaurants($restaurantListInput: RestaurantListInput!) {
              restaurants: restaurantList(input: $restaurantListInput) {
                total
                items {
                  category
                  id
                  name
                }
              }
            }
            '''

        self.variables = {
             "restaurantListInput": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "takeout": None,
                "orderBenefit": None,
                "isCurrentLocationSearch": None,
                "filterOpening": None,
                "deviceType": "pcmap",
                "bounds": "500",
                "isPcmap": True
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getHospital(self):
        self.query = '''
            query getNxList($input: HospitalListInput!) {
                businesses: hospitals(input: $input) {
                    total
                    items {
                        category
                        id
                        name
                    }
                }
            }
        '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "deviceType": "pcmap",
                "bounds": "500"
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getTrip(self):
        self.query = '''
            query getTrips($input: TripsInput!) {
               businesses: trips(input: $input) {
                    total
                    items {
                        category
                        id
                        name
                    }
                }
            }
        '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "deviceType": "pcmap",
                "bounds": "500"
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getRestaurant(self):
        self.query = '''
            query getRestaurants($restaurantListInput: RestaurantListInput!) {
              restaurants: restaurantList(input: $restaurantListInput) {
                total
                items {
                  category
                  id
                  name
                }
              }
            }
            '''

        self.variables = {
             "restaurantListInput": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "takeout": None,
                "orderBenefit": None,
                "isCurrentLocationSearch": None,
                "filterOpening": None,
                "deviceType": "pcmap",
                "bounds": "500",
                "isPcmap": True
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getHairshop(self):
        self.query = '''
           query getBeautyList($input: BeautyListInput!) {
               businesses: hairshops(input: $input) {
                   total
                   items {
                       category
                       id
                       name
                   }               
               }
           }
       '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "deviceType": "pcmap",
                "bounds": "500"
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getNailshop(self):
        self.query = '''
           query getBeautyList($input: BeautyListInput!) {
               businesses: nailshops(input: $input) {
                   total
                   items {
                       category
                       id
                       name
                   }               
               }
           }
       '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "deviceType": "pcmap",
                "bounds": "500"
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getAccommodation(self):
        self.query = '''
           query getAccommodationList($input: AccommodationListInput!) {
               businesses: accommodations(input: $input) {
                   total
                   items {
                       category
                       id
                       name
                   }               
               }
           }
       '''

        self.variables = {
            "input": {
                "query": self.keyword,
                "x": self.locationX,
                "y": self.locationY,
                "start": self.start,
                "display": 50,
                "deviceType": "pcmap",
                "bounds": "500"
            },
            "useReverseGeocode": True,
            "isNmap": False
        }

    def getGolf(self):
        self.query = '''
           query attractionList($input: AttractionsInput!, $businessesInput: AttractionsBusinessesInput) {
               attractions(input: $input) {
                   businesses(input: $businessesInput) {
                       total
                       items {
                           id
                           name
                       }
                   }
               }
           }
       '''

        self.variables = {
            "input": {
                "keyword": self.keyword,
                "region": None,
                "isBrandList": None,
                "filterBooking": False,
                "hasNearQuery": None
            },
            "businessesInput": {
                "start": self.start,
                "display": 50,
                "x": self.locationX,
                "y": self.locationY,
                "deviceType": "pcmap",
                "bounds": "500",
                "sortingOrder": "precision"
            }
        }
