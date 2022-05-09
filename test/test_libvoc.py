from unittest import IsolatedAsyncioTestCase

import data_api.lib_voc as OJVoc
import httpx


class TestLibVocFunctions(IsolatedAsyncioTestCase):

    async def test_setArkUrl(self):
        r = await OJVoc.setArkUrl('poulet', 'mayonnaise')
        self.assertEqual(r, None)

    async def testgetArkUrl(self):
        # TODO : Use a mock & decorator maybe
        ark = await OJVoc.getArkId('http://example.com/OjTestingUrl')
        r = httpx.get(f"https://n2d.eu/{ark}")
        # Ark is a redirect
        self.assertEqual(r.status_code, 302)
