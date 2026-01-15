'use client'

import { Box, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'
import dynamic from 'next/dynamic'

const ConfigTab = dynamic(() => import('../components/ConfigTab'), {
  ssr: false,
})

const EpisodesTab = dynamic(() => import('../components/EpisodesTab'), {
  ssr: false,
})

const InterviewPrepTab = dynamic(() => import('../components/InterviewPrepTab'), {
  ssr: false,
})

export default function Home() {
  return (
    <Box as="main" dir="rtl" p={4}>
      <Box as="h1" fontSize="2xl" mb={4} textAlign="center">הסכתומאט</Box>
      <Tabs defaultIndex={2}>
        <TabList>
          <Tab>הגדרות</Tab>
          <Tab>פרקים</Tab>
          <Tab>הכנה לראיון</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <ConfigTab />
          </TabPanel>
          <TabPanel>
            <EpisodesTab />
          </TabPanel>
          <TabPanel>
            <InterviewPrepTab />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}