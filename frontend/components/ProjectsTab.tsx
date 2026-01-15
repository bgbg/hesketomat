'use client'

import { useState } from 'react'
import {
  Box,
  SimpleGrid,
  Text,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Button,
  VStack,
  HStack,
  Badge,
  IconButton,
  Icon,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Container,
  Flex,
} from '@chakra-ui/react'

// Mock icons
const FolderIcon = (props: any) => <Box as="span" fontSize="2xl" {...props}>📁</Box>
const MoreIcon = (props: any) => <Box as="span" {...props}>⋮</Box>
const AddIcon = (props: any) => <Box as="span" {...props}>➕</Box>
const TimeIcon = (props: any) => <Box as="span" {...props}>🕒</Box>
const TrashIcon = (props: any) => <Box as="span" {...props}>🗑️</Box>

// Type definition matching the structure used in InterviewPrepTab
interface Project {
  id: string
  title: string
  lastModified: string
  noteCount: number
  hasContext: boolean
}

// Key for localStorage (must match InterviewPrepTab if we were sharing a single store,
// but here we likely want a 'projects_index' separate from the 'current_workspace')
const PROJECTS_KEY = 'hesketomat_projects_index'

export default function ProjectsTab({ onLoadProject, onNewProject }: { onLoadProject: (id: string) => void, onNewProject: () => void }) {
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // Mock data for visualization - in a real app this would load from localStorage/API
  const [projects, setProjects] = useState<Project[]>([
    {
      id: 'p1',
      title: 'ראיון עם יוסי כהן - מנכ״ל סטארטאפ',
      lastModified: new Date().toISOString(),
      noteCount: 12,
      hasContext: true,
    },
    {
      id: 'p2',
      title: 'תחקיר על בינה מלאכותית בחינוך',
      lastModified: new Date(Date.now() - 86400000).toISOString(),
      noteCount: 5,
      hasContext: false,
    },
    {
      id: 'p3',
      title: 'שיחת הכנה - פרק 42',
      lastModified: new Date(Date.now() - 172800000).toISOString(),
      noteCount: 8,
      hasContext: true,
    }
  ])

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('האם אתה בטוח שברצונך למחוק את הפרוייקט?')) {
        setProjects(projects.filter(p => p.id !== id))
    }
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Flex justify="space-between" align="center" mb={8}>
          <Heading size="lg">הפרוייקטים שלי</Heading>
          <Button leftIcon={<AddIcon />} colorScheme="purple" onClick={onNewProject}>
              פרוייקט חדש
          </Button>
      </Flex>

      {projects.length === 0 ? (
          <Box textAlign="center" py={10} color="gray.500" border="2px dashed" borderColor={borderColor} borderRadius="lg">
              <FolderIcon fontSize="4xl" mb={4} display="block" />
              <Text fontSize="lg" mb={4}>אין עדיין פרוייקטים</Text>
              <Button colorScheme="blue" onClick={onNewProject}>צור את הראשון!</Button>
          </Box>
      ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {projects.map((project) => (
              <Card
                key={project.id}
                bg={cardBg}
                shadow="sm"
                _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
                transition="all 0.2s"
                cursor="pointer"
                onClick={() => onLoadProject(project.id)}
                border="1px solid"
                borderColor={borderColor}
              >
                <CardHeader pb={2}>
                    <Flex justify="space-between" align="start">
                        <HStack spacing={3}>
                            <Box p={2} bg="blue.50" borderRadius="md" color="blue.500">
                                <FolderIcon fontSize="xl" />
                            </Box>
                            <Box>
                                <Heading size="md" noOfLines={1} title={project.title}>
                                    {project.title}
                                </Heading>
                                <HStack fontSize="xs" color="gray.500" mt={1}>
                                    <TimeIcon />
                                    <Text>{new Date(project.lastModified).toLocaleDateString('he-IL')}</Text>
                                </HStack>
                            </Box>
                        </HStack>
                        <Menu>
                            <MenuButton
                                as={IconButton}
                                icon={<MoreIcon />}
                                variant="ghost"
                                size="sm"
                                aria-label="options"
                                onClick={(e) => e.stopPropagation()}
                            />
                            <MenuList>
                                <MenuItem icon={<TrashIcon />} onClick={(e) => handleDelete(project.id, e as any)} color="red.500">
                                    מחק
                                </MenuItem>
                            </MenuList>
                        </Menu>
                    </Flex>
                </CardHeader>
                <CardBody pt={2}>
                    <HStack spacing={2}>
                        <Badge colorScheme="gray">{project.noteCount} פתקים</Badge>
                        {project.hasContext && <Badge colorScheme="green">יש קונטקסט</Badge>}
                    </HStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
      )}
    </Container>
  )
}
