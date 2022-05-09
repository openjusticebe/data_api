from unittest import IsolatedAsyncioTestCase

import data_api.lib_voc as OJVoc
import httpx


class TestLibVocFunctions(IsolatedAsyncioTestCase):

    async def testgetArkUrl(self):
        # TODO : Use a mock & decorator maybe
        testUrl = 'http://example.com/OjTestingUrl'
        ark = await OJVoc.getArkId(testUrl)
        r = httpx.get(f"https://n2d.eu/{ark}")
        # Ark is a redirect
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers.get('location'), testUrl)

    async def testSetArkUrl(self):
        testArk = "ark:/36598/OJh49jgcjtt"
        testUrl1 = 'http://example.com/OjTestingUrl'
        testUrl2 = 'http://example.com/OjTestingUrl2'

        await OJVoc.setArkUrl(testArk, testUrl1)
        r = httpx.get(f"https://n2d.eu/{testArk}")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers.get('location'), testUrl1)

        await OJVoc.setArkUrl(testArk, testUrl2)
        r = httpx.get(f"https://n2d.eu/{testArk}")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers.get('location'), testUrl2)

    async def testSetVocLinks(self):
        docId = 'http://example.com/un_nom'
        vocIds = [
            'http://example.com/terme_un',
            'http://example.com/terme_deux'
        ]

        await OJVoc.setLinks(docId, vocIds)

        getList = await OJVoc.getLinks(docId)

        self.assertEqual(vocIds, getList)
