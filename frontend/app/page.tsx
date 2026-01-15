'use client'

import { Box, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'
import { useState } from 'react'
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



const ProjectsTab = dynamic(() => import('../components/ProjectsTab'), {
  ssr: false,
})

export default function Home() {
  // Use state to control the active tab index if needed,
  // but better yet, let's control the view inside the Interview Prep flow if we want "Projects" to be a separate main tab or a sub-state.
  // Based on request: "Save page I see... start another episode... all saved projects are in Projects... clicking loads it"
  // It sounds like "Projects" should be a top-level tab that MANAGRES what is loaded into "Preparation".

  // However, simpler for now: Just add the tab.
  const [tabIndex, setTabIndex] = useState(3) // Default to Projects (index 3) to show it off? Or 2? Let's use 2 as requested before, but now we have 4 tabs.

  // We need a way to pass data between ProjectsTab and InterviewPrepTab.
  // For this mockup, we'll just simulate the switch.

  const handleLoadProject = (projectId: string) => {
      // In a real app, this would set a Global Context or URL param.
      // For now, we just switch to the Prep tab (Index 3).
      // The PrepTab would ideally read the "currentProjectId" from somewhere.
      setTabIndex(3)
  }

  const handleNewProject = () => {
      setTabIndex(3)
  }

  return (
    <Box as="main" dir="rtl" p={4}>
      <Box as="h1" fontSize="2xl" mb={4} textAlign="center">הסכתומאט</Box>
      <Tabs index={tabIndex} onChange={(index) => setTabIndex(index)}>
        <TabList>
          <Tab>הגדרות</Tab>
          <Tab>פרקים</Tab>
          <Tab>פרוייקטים</Tab>
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
             <ProjectsTab onLoadProject={handleLoadProject} onNewProject={handleNewProject} />
          </TabPanel>
          <TabPanel>
            <InterviewPrepTab />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}