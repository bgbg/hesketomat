'use client'

import { useState } from 'react'
import {
  Box,
  Flex,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  IconButton,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Divider,
  Badge,
  InputGroup,
  InputRightElement,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  Textarea,
  useColorModeValue,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Tooltip,
  Image,
} from '@chakra-ui/react'

// Mock Icons since we don't have an icon library installed
const SearchIcon = (props: any) => <Box as="span" {...props}>🔍</Box>
const AddIcon = (props: any) => <Box as="span" {...props}>➕</Box>
const MoreIcon = (props: any) => <Box as="span" {...props}>⋮</Box>
const LinkIcon = (props: any) => <Box as="span" {...props}>🔗</Box>
const DragHandleIcon = (props: any) => <Box as="span" cursor="grab" color="gray.400" {...props}>☰</Box>
const SaveIcon = (props: any) => <Box as="span" {...props}>💾</Box>
const MagicIcon = (props: any) => <Box as="span" {...props}>✨</Box>

export default function InterviewPrepTab() {
  const [searchQuery, setSearchQuery] = useState('')
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // --- Mock Data ---
  const [interviewTitle, setInterviewTitle] = useState('ראיון עם יוסי כהן - מנכ״ל סטארטאפ')

  const notes = [
    {
      id: '1',
      title: 'רקע וביוגרפיה',
      type: 'bucket',
      items: [
        { id: '1a', type: 'text', content: 'שירת ב-8200 במשך 5 שנים', provenance: 'web', source: { title: 'LinkedIn Profile', domain: 'linkedin.com' } },
        { id: '1b', type: 'text', content: 'הקים את החברה בשנת 2019', provenance: 'manual' },
      ]
    },
    {
      id: '2',
      title: 'נושאי שיחה עיקריים',
      type: 'bucket',
      items: [
        { id: '2a', type: 'text', content: 'אתגרי גיוס כספים בתקופה הנוכחית', provenance: 'web', source: { title: 'TechCrunch Article', domain: 'techcrunch.com' } },
      ]
    }
  ]

  const searchResults = {
    summary: 'יוסי כהן הוא יזם טכנולוגי סדרתי. החברה האחרונה שלו, TechFlow, גייסה לאחרונה 50 מיליון דולר בסבב B. הוא ידוע בגישתו הייחודית לניהול מוצר ופיתוח צוותים מבוזרים.',
    web: [
      { id: 'w1', title: 'ראיון עומק עם יוסי כהן על עתיד ה-AI', domain: 'calcalist.co.il', snippet: 'בשיחה גלויה חושף כהן את התוכניות שלו לעתיד...' },
      { id: 'w2', title: 'TechFlow מגייסת 50 מיליון דולר', domain: 'globes.co.il', snippet: 'הסטארטאפ המבטיח ממשיך לצמוח למרות המשבר...' },
    ]
  }

  const outline = [
    { id: 'o1', type: 'heading', level: 1, text: 'פתיחה והצגה (5 דקות)' },
    { id: 'o2', type: 'paragraph', text: 'הצגת האורח והרקע הקצר שלו. לשאול על המעבר משירות צבאי ליזמות.' },
    { id: 'o3', type: 'heading', level: 1, text: 'הקמת TechFlow' },
    { id: 'o4', type: 'paragraph', text: 'מה היה הרגע שבו הבנת שיש צורך במוצר הזה? איך גייסתם את הצוות הראשון?' },
  ]

  return (
    <Box h="calc(100vh - 150px)" display="flex" flexDirection="column" overflow="hidden">
      {/* --- Top Bar --- */}
      <Flex
        h="60px"
        align="center"
        justify="space-between"
        px={4}
        borderBottom="1px"
        borderColor={borderColor}
        bg={cardBg}
      >
        <HStack spacing={4}>
            <Input
                value={interviewTitle}
                onChange={(e) => setInterviewTitle(e.target.value)}
                fontWeight="bold"
                fontSize="lg"
                variant="unstyled"
                w="400px"
            />
            <Badge colorScheme="green" variant="subtle"><SaveIcon /> נשמר</Badge>
        </HStack>
        <HStack>
            <Button size="sm" leftIcon={<MagicIcon />} colorScheme="purple" variant="ghost">צור אאוטליין</Button>
            <Button size="sm" variant="ghost">ייצוא</Button>
            <Button size="sm" variant="ghost">עזרה</Button>
        </HStack>
      </Flex>

      {/* --- 3-Column Layout --- */}
      <Flex flex="1" overflow="hidden">

        {/* --- Left Column: Notes --- */}
        <Box w="30%" minW="250px" bg={bgColor} borderRight="1px" borderColor={borderColor} display="flex" flexDirection="column">
            <Flex p={3} justify="space-between" align="center" bg={cardBg} borderBottom="1px" borderColor={borderColor}>
                <Text fontWeight="bold" color="gray.600">פתקים ומחקר</Text>
                <Button size="xs" leftIcon={<AddIcon />} colorScheme="blue" variant="solid">פתק חדש</Button>
            </Flex>
            <VStack p={3} spacing={3} overflowY="auto" flex="1" align="stretch">
                {notes.map(note => (
                    <Card key={note.id} size="sm" shadow="sm" borderRadius="md" _hover={{ shadow: 'md' }}>
                        <CardHeader p={2} pb={1} display="flex" justifyContent="space-between" alignItems="center">
                            <HStack>
                                <DragHandleIcon />
                                <Text fontWeight="bold" fontSize="sm">{note.title}</Text>
                            </HStack>
                            <IconButton aria-label="options" icon={<MoreIcon />} size="xs" variant="ghost" />
                        </CardHeader>
                        <CardBody p={2} pt={0}>
                            <VStack spacing={2} align="stretch" mt={2}>
                                {note.items.map(item => (
                                    <Box key={item.id} p={2} bg="gray.50" borderRadius="md" fontSize="sm" border="1px solid" borderColor="gray.100">
                                        <Text fontSize="xs" mb={1}>{item.content}</Text>
                                        {item.provenance === 'web' && (
                                            <HStack spacing={1} mt={1} color="blue.500" fontSize="10px">
                                                <LinkIcon />
                                                <Text>{item.source?.domain}</Text>
                                            </HStack>
                                        )}
                                    </Box>
                                ))}
                            </VStack>
                        </CardBody>
                    </Card>
                ))}

                {/* Empty State / Add note hint */}
                <Box border="1px dashed" borderColor="gray.300" borderRadius="md" p={4} textAlign="center" color="gray.500" cursor="pointer" _hover={{ bg: 'gray.100' }}>
                    <Text fontSize="sm">+ גרור לכאן טקסט או לחץ להוספה</Text>
                </Box>
            </VStack>
        </Box>

        {/* --- Middle Column: Search --- */}
        <Box w="35%" minW="300px" bg="white" borderRight="1px" borderColor={borderColor} display="flex" flexDirection="column">
             <Box p={4} borderBottom="1px" borderColor={borderColor}>
                 <InputGroup size="md">
                    <Input
                        placeholder="שאל שאלה או חפש נושא..."
                        bg="gray.50"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        borderRadius="full"
                    />
                    <InputRightElement>
                        <Button size="sm" borderRadius="full" colorScheme="blue" variant="ghost"><SearchIcon /></Button>
                    </InputRightElement>
                 </InputGroup>
             </Box>

             <Box flex="1" overflowY="auto" p={4}>
                {searchQuery || true ? ( // Mocking active search state
                    <VStack spacing={4} align="stretch">
                        {/* LLM Summary */}
                        <Box bg="purple.50" p={4} borderRadius="lg" border="1px solid" borderColor="purple.100">
                            <HStack mb={2} color="purple.700">
                                <MagicIcon />
                                <Text fontWeight="bold" fontSize="sm">תקציר AI</Text>
                            </HStack>
                            <Text fontSize="sm" color="gray.800" lineHeight="tall">
                                {searchResults.summary}
                            </Text>
                            <HStack mt={3} spacing={2}>
                                {['calcalist.co.il', 'globes.co.il'].map((cite, i) => (
                                    <Badge key={i} variant="outline" colorScheme="purple" fontSize="xs" cursor="pointer">[{i+1}] {cite}</Badge>
                                ))}
                            </HStack>
                        </Box>

                        <Divider />

                        <Text fontWeight="bold" fontSize="sm" color="gray.500">תוצאות חיפוש</Text>

                        {/* Web Results */}
                        {searchResults.web.map(res => (
                            <Box key={res.id} p={3} borderRadius="md" _hover={{ bg: 'gray.50' }} transition="all 0.2s">
                                <Text color="blue.600" fontWeight="bold" fontSize="sm" cursor="pointer" _hover={{ textDecoration: 'underline' }}>
                                    {res.title}
                                </Text>
                                <HStack spacing={2} fontSize="xs" color="gray.500" mb={1}>
                                    <Avatar size="2xs" name={res.domain} src={`https://www.google.com/s2/favicons?domain=${res.domain}`} />
                                    <Text>{res.domain}</Text>
                                </HStack>
                                <Text fontSize="xs" color="gray.600" noOfLines={2}>{res.snippet}</Text>
                                <HStack mt={2}>
                                    <Button size="xs" variant="outline" leftIcon={<AddIcon />}>הוסף לפתק</Button>
                                </HStack>
                            </Box>
                        ))}

                        {/* Image Results (Mock Grid) */}
                        <Text fontWeight="bold" fontSize="sm" color="gray.500" mt={2}>תמונות</Text>
                        <HStack spacing={2} overflowX="auto" pb={2}>
                            {[1, 2, 3].map(i => (
                                <Box key={i} minW="100px" h="80px" bg="gray.200" borderRadius="md" position="relative" role="group">
                                    <Image
                                        src={`https://placehold.co/100x80?text=Img+${i}`}
                                        alt="result"
                                        objectFit="cover"
                                        w="full"
                                        h="full"
                                        borderRadius="md"
                                    />
                                    <Box
                                        position="absolute"
                                        top={0} left={0} right={0} bottom={0}
                                        bg="blackAlpha.600"
                                        display="none"
                                        _groupHover={{ display: 'flex' }}
                                        alignItems="center"
                                        justifyContent="center"
                                        borderRadius="md"
                                    >
                                        <Button size="xs" colorScheme="whiteAlpha" variant="solid"><AddIcon /></Button>
                                    </Box>
                                </Box>
                            ))}
                        </HStack>

                    </VStack>
                ) : (
                    <Flex h="full" align="center" justify="center" direction="column" color="gray.400">
                        <SearchIcon size="40px" /> {/* Pseudo size */}
                        <Text mt={4}>חפש נושא כדי להתחיל...</Text>
                    </Flex>
                )}
             </Box>
        </Box>

        {/* --- Right Column: Outline Canvas --- */}
        <Box w="35%" minW="300px" bg={cardBg} display="flex" flexDirection="column">
            <Flex p={3} borderBottom="1px" borderColor={borderColor} justify="space-between" bg={useColorModeValue("white", "gray.800")}>
                <Text fontWeight="bold">אאוטליין לראיון</Text>
                <HStack>
                    <Tooltip label="עורך טקסט חכם"><Badge>Smart Editor</Badge></Tooltip>
                </HStack>
            </Flex>
            <Box flex="1" overflowY="auto" p={6} className="outline-editor">
                <VStack align="stretch" spacing={4}>
                    {outline.map(block => (
                        <Box key={block.id} position="relative" _hover={{ '& .block-handle': { opacity: 1 } }}>
                            {/* Hover Handle */}
                            <Box position="absolute" right="-20px" top="0" className="block-handle" opacity={0} cursor="grab" p={1}>
                                <DragHandleIcon />
                            </Box>

                            {block.type === 'heading' ? (
                                <Input
                                    defaultValue={block.text}
                                    fontWeight="bold"
                                    fontSize="lg"
                                    variant="unstyled"
                                    placeholder="כותרת..."
                                />
                            ) : (
                                <Textarea
                                    defaultValue={block.text}
                                    variant="unstyled"
                                    resize="none"
                                    overflow="hidden"
                                    minH="20px"
                                    p={0}
                                    placeholder="כתוב כאן..."
                                    fontSize="md"
                                />
                            )}
                        </Box>
                    ))}
                    {/* New block placeholder */}
                     <Box opacity={0.5} _hover={{ opacity: 1 }} cursor="text">
                        <Text>+ הקלד כדי להוסיף סעיף חדש...</Text>
                    </Box>
                </VStack>
            </Box>

            {/* Selection Toolbar Mockup (Floating) */}
            <Box
                position="absolute"
                bottom="50px"
                left="20%"
                bg="gray.800"
                color="white"
                p={2}
                borderRadius="md"
                shadow="lg"
                display="none" // Hidden by default, imagine text selection triggers it
            >
                <HStack spacing={2}>
                    <Button size="xs" variant="ghost" colorScheme="whiteAlpha">שפר</Button>
                    <Button size="xs" variant="ghost" colorScheme="whiteAlpha">קצר</Button>
                    <Button size="xs" variant="ghost" colorScheme="whiteAlpha">שנה טון</Button>
                </HStack>
            </Box>
        </Box>
      </Flex>
    </Box>
  )
}
