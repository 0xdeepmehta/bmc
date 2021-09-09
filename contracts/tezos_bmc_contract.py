import smartpy as sp

class BuyMeCrypto(sp.Contract):
    def __init__(self):
        self.init(
            creators = sp.big_map(
                tkey = sp.TNat,
                tvalue = sp.TRecord(
                    owner = sp.TAddress,
                    balance = sp.TMutez
                )
            ),

            supporters = sp.big_map(
                tkey = sp.TRecord(
                    creator_id = sp.TNat,
                    supporter_id = sp.TAddress
                ),
                tvalue = sp.TMutez
            )   
        )

    @sp.entry_point
    def create_creator_account(self, creator_id, contentType):
        """ Create new creator account """
        sp.verify(~ self.data.creators.contains(creator_id)) # checking if creator is already registered

        self.data.creators[creator_id] = sp.record(owner=sp.sender, contentType=contentType, balance=sp.mutez(0))

    @sp.entry_point
    def support_creator(self, creator_id):
        """ Support Favourite Creator """
        sp.verify(self.data.creators.contains(creator_id))
        self.data.supporters[sp.record(creator_id=creator_id, supporter_id=sp.sender)] = sp.amount
        self.data.creators[creator_id].balance += sp.amount


    @sp.entry_point
    def withdraw_funds(self, creator_id):
        """ It allow the owner of a creator_id to withdraw the funds. """
        sp.verify(self.data.creators.contains(creator_id)) # verify if the creator_id exists

        sp.verify(self.data.creators[creator_id].owner == sp.sender) # verify if sender/reciever is the owner of the cause

        sp.send(self.data.creators[creator_id].owner, self.data.creators[creator_id].balance) # Transfer the collected funds

        # Reset the amount as it's withdrawn now.
        self.data.creators[creator_id].balance = sp.mutez(0)


@sp.add_test("Buy Me Crypto")
def test():
    """ Testing contract """

    scenario = sp.test_scenario()
    bcm = BuyMeCrypto()

    creator = sp.test_account("Owner")
    supporter1 = sp.test_account("Supporter 1")
    supporter2 = sp.test_account("supporter 2")

    scenario += bcm
    scenario += bcm.create_creator_account(creator_id=1, contentType="Creator of blockchain").run(sender=creator)

    # Let's support the creator
    scenario += bcm.support_creator(1).run(sender=supporter1, amount=sp.mutez(1000000))

    # Let's verify the amount
    scenario.verify(bcm.data.creators[1].balance == sp.mutez(1000000))

    # should raise an error if we try to create new creator account with existing creator_id

    scenario += bcm.create_creator_account(creator_id=1, contentType="Creator of bitcoin").run(sender=creator, valid=False)

    # withdraw funds
    # Should raise error
    scenario += bcm.withdraw_funds(1).run(sender=supporter1, valid=False)

    # with correct owner

    scenario += bcm.withdraw_funds(1).run(sender=creator)
