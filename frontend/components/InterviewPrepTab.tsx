'use client'

import { useState, useEffect } from 'react'
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
  useToast,
} from '@chakra-ui/react'
import { Reorder, useDragControls } from 'framer-motion'

// Mock Icons
const SearchIcon = (props: any) => <Box as="span" {...props}>🔍</Box>
const AddIcon = (props: any) => <Box as="span" {...props}>➕</Box>
const MoreIcon = (props: any) => <Box as="span" {...props}>⋮</Box>
const LinkIcon = (props: any) => <Box as="span" {...props}>🔗</Box>
const DragHandle = ({ controls }: { controls: any }) => (
  <Box
    as="span"
    cursor="grab"
    color="gray.400"
    onPointerDown={(e) => controls.start(e)}
    _active={{ cursor: "grabbing" }}
  >
    ☰
  </Box>
)
const DragHandleIcon = (props: any) => <Box as="span" cursor="grab" color="gray.400" {...props}>☰</Box>
const SaveIcon = (props: any) => <Box as="span" {...props}>💾</Box>
const MagicIcon = (props: any) => <Box as="span" {...props}>✨</Box>
const SettingsIcon = (props: any) => <Box as="span" {...props}>⚙️</Box>
const ChevronDownIcon = (props: any) => <Box as="span" {...props}>▼</Box>
const RepeatIcon = (props: any) => <Box as="span" {...props}>🔄</Box>
const FileIcon = (props: any) => <Box as="span" {...props}>📄</Box>

const NoteItem = ({ note, notes, setNotes, isSelected, onSelect }: { note: any, notes: any[], setNotes: any, isSelected: boolean, onSelect: () => void }) => {
  const dragControls = useDragControls()
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const selectedBorderColor = useColorModeValue('blue.500', 'blue.300')
  const selectedBg = useColorModeValue('blue.50', 'blue.900')

  return (
    <Reorder.Item value={note} dragListener={false} dragControls={dragControls} style={{ listStyle: 'none' }}>
        <Card
            size="sm"
            shadow={isSelected ? 'md' : 'sm'}
            borderRadius="md"
            borderWidth="2px"
            borderColor={isSelected ? selectedBorderColor : 'transparent'}
            bg={isSelected ? selectedBg : undefined}
            _hover={{ shadow: 'md', borderColor: isSelected ? selectedBorderColor : borderColor }}
            onClick={onSelect}
            cursor="pointer"
        >
            <CardHeader p={2} pb={1} display="flex" justifyContent="space-between" alignItems="center">
                <HStack>
                    <DragHandle controls={dragControls} />
                    <Input
                      value={note.title}
                      onChange={(e) => {
                          const newNotes = notes.map((n: any) => n.id === note.id ? { ...n, title: e.target.value } : n)
                          setNotes(newNotes)
                      }}
                      fontWeight="bold"
                      fontSize="sm"
                      variant="unstyled"
                      w="200px"
                      onClick={(e) => e.stopPropagation()}
                    />
                </HStack>
                <IconButton aria-label="options" icon={<MoreIcon />} size="xs" variant="ghost" />
            </CardHeader>
            <CardBody p={2} pt={0}>
                <VStack spacing={2} align="stretch" mt={2}>
                    {note.items.map((item: any) => (
                        <Box key={item.id} p={2} bg="white" _dark={{ bg: 'gray.700' }} borderRadius="md" fontSize="sm" border="1px solid" borderColor="gray.100">
                             {item.type === 'image' ? (
                                <Image src={item.content} alt="clip" boxSize="100px" objectFit="cover" borderRadius="sm" />
                             ) : (
                                <Text fontSize="xs" mb={1}>{item.content}</Text>
                             )}

                             {item.provenance === 'web' && (
                                 <HStack spacing={1} mt={1} color="blue.500" fontSize="10px">
                                     <LinkIcon />
                                     <Text>{item.source?.domain}</Text>
                                 </HStack>
                             )}
                        </Box>
                    ))}
                    <Box
                        border="1px dashed"
                        borderColor="gray.300"
                        borderRadius="md"
                        h="30px"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        fontSize="xs"
                        color="gray.500"
                    >
                        גרור לכאן פריטים
                    </Box>
                </VStack>
            </CardBody>
        </Card>
    </Reorder.Item>
  )
}

const STORAGE_KEY = 'interview_prep_state'

export default function InterviewPrepTab() {
  const [searchQuery, setSearchQuery] = useState('')
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const toast = useToast()

  // --- State ---
  const [interviewTitle, setInterviewTitle] = useState('ראיון חדש')
  const [backgroundContext, setBackgroundContext] = useState('')
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  const [notes, setNotes] = useState<any[]>([])

  // Selection state
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null)

  const [outline, setOutline] = useState<any[]>([
    { id: 'o1', type: 'heading', level: 1, text: 'פתיחה והצגה (5 דקות)' },
    { id: 'o2', type: 'paragraph', text: 'הצגת האורח והרקע הקצר שלו.' },
  ])

  // Initial Load / Mock Data Setup
  useEffect(() => {
    // Check for saved data or load initial mock data if empty
    const savedData = localStorage.getItem(STORAGE_KEY)
    if (savedData) {
        try {
            const parsed = JSON.parse(savedData)
            setInterviewTitle(parsed.interviewTitle)
            setBackgroundContext(parsed.backgroundContext)
            setNotes(parsed.notes)
            setOutline(parsed.outline)
            setLastSaved(new Date(parsed.timestamp))
            if(parsed.notes.length > 0) setSelectedNoteId(parsed.notes[0].id)
        } catch (e) {
            console.error("Failed to load saved state", e)
        }
    } else {
        // Load default mock data
        setInterviewTitle('ראיון עם יוסי כהן - מנכ״ל סטארטאפ')
        setNotes([
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
        ])
        setOutline([
            { id: 'o1', type: 'heading', level: 1, text: 'פתיחה והצגה (5 דקות)' },
            { id: 'o2', type: 'paragraph', text: 'הצגת האורח והרקע הקצר שלו. לשאול על המעבר משירות צבאי ליזמות.' },
            { id: 'o3', type: 'heading', level: 1, text: 'הקמת TechFlow' },
            { id: 'o4', type: 'paragraph', text: 'מה היה הרגע שבו הבנת שיש צורך במוצר הזה? איך גייסתם את הצוות הראשון?' },
        ])
    }
  }, [])

  // Auto-select first note if none selected
  useEffect(() => {
    if (notes.length > 0 && !selectedNoteId) {
        setSelectedNoteId(notes[0].id)
    }
  }, [notes, selectedNoteId])

  const searchResults = {
    summary: 'יוסי כהן הוא יזם טכנולוגי סדרתי. החברה האחרונה שלו, TechFlow, גייסה לאחרונה 50 מיליון דולר בסבב B. הוא ידוע בגישתו הייחודית לניהול מוצר ופיתוח צוותים מבוזרים.',
    web: [
      { id: 'w1', title: 'ראיון עומק עם יוסי כהן על עתיד ה-AI', domain: 'calcalist.co.il', snippet: 'בשיחה גלויה חושף כהן את התוכניות שלו לעתיד...' },
      { id: 'w2', title: 'TechFlow מגייסת 50 מיליון דולר', domain: 'globes.co.il', snippet: 'הסטארטאפ המבטיח ממשיך לצמוח למרות המשבר...' },
    ],
    images: [1, 2, 3].map(i => ({ id: `img${i}`, src: `https://placehold.co/100x80?text=Img+${i}`, domain: 'google.com' }))
  }

  // --- Actions ---

  const handleSave = () => {
    const state = {
        interviewTitle,
        backgroundContext,
        notes,
        outline,
        timestamp: new Date().toISOString()
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    setLastSaved(new Date())
    toast({
        title: "נשמר בהצלחה",
        status: "success",
        duration: 2000,
        isClosable: true,
    })
  }

  const handleReload = () => {
     // Trigger page reload or re-read local storage
     window.location.reload()
  }

  const handleNew = () => {
      if (confirm("האם אתה בטוח שברצונך להתחיל ראיון חדש? כל השינויים שלא נשמרו יאבדו.")) {
          setInterviewTitle('ראיון חדש')
          setBackgroundContext('')
          setNotes([])
          setOutline([
            { id: 'o1', type: 'heading', level: 1, text: 'פתיחה' },
          ])
          setSelectedNoteId(null)
          localStorage.removeItem(STORAGE_KEY) // Clear saved state? Or keep distinct IDs? For now clear key.
          toast({ title: "נוצר ראיון חדש", status: "info", duration: 2000 })
      }
  }

  const handleAddToNote = (item: any) => {
      let targetNoteIndex = -1
      if (selectedNoteId) {
          targetNoteIndex = notes.findIndex(n => n.id === selectedNoteId)
      }

      // If no valid note selected, create one
      let newNotes = [...notes]
      if (targetNoteIndex === -1) {
          const newNoteId = Math.random().toString(36).substr(2, 9)
          newNotes.push({
              id: newNoteId,
              title: 'פתק כללי',
              type: 'bucket',
              items: []
          })
          targetNoteIndex = newNotes.length - 1
          setSelectedNoteId(newNoteId)
      }

      const newId = Math.random().toString(36).substr(2, 9)
      newNotes[targetNoteIndex].items.push({
          id: newId,
          type: item.type || 'text',
          content: item.content || item.src,
          provenance: 'web',
          source: { title: item.title || 'Image', domain: item.domain || 'web' }
      })

      setNotes(newNotes)
      toast({
          title: "נוסף לפתק",
          description: `הפריט נוסף ל"${newNotes[targetNoteIndex].title}"`,
          status: "success",
          duration: 2000,
      })
  }

  const updateOutlineBlock = (id: string, text: string) => {
      setOutline(outline.map(b => b.id === id ? { ...b, text } : b))
  }

  const addOutlineBlock = () => {
      const newBlock = { id: Math.random().toString(36).substr(2, 9), type: 'paragraph', text: '' }
      setOutline([...outline, newBlock])
  }

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
            {/* Main Menu */}
            <Menu>
                <MenuButton as={Button} leftIcon={<FileIcon />} rightIcon={<ChevronDownIcon variant="outline" />} size="sm">
                    תפריט
                </MenuButton>
                <MenuList zIndex={10}>
                    <MenuItem icon={<AddIcon />} onClick={handleNew}>ראיון חדש</MenuItem>
                    <MenuItem icon={<SaveIcon />} onClick={handleSave}>שמור שינויים</MenuItem>
                    <MenuItem icon={<RepeatIcon />} onClick={handleReload}>טען מחדש</MenuItem>
                </MenuList>
            </Menu>

            <Divider orientation="vertical" h="20px" />

            <Input
                value={interviewTitle}
                onChange={(e) => setInterviewTitle(e.target.value)}
                fontWeight="bold"
                fontSize="lg"
                variant="unstyled"
                w="400px"
            />
            {lastSaved && <Badge colorScheme="green" variant="subtle" fontSize="xs">נשמר ב: {lastSaved.toLocaleTimeString()}</Badge>}
        </HStack>
        <HStack>
            <Button size="sm" leftIcon={<MagicIcon />} colorScheme="purple" variant="ghost">צור אאוטליין</Button>
            <Button size="sm" variant="ghost">ייצוא</Button>
            <Button size="sm" variant="ghost">עזרה</Button>
        </HStack>
      </Flex>

      {/* --- 3-Column Layout --- */}
      <Flex flex="1" overflow="hidden">

        {/* --- Left Column: Notes & Context --- */}
        <Box w="30%" minW="250px" bg={bgColor} borderRight="1px" borderColor={borderColor} display="flex" flexDirection="column">

            {/* Context Area - Always Visible */}
            <Box p={3} borderBottom="1px" borderColor={borderColor} bg="yellow.50">
                 <Text fontSize="xs" fontWeight="bold" color="yellow.700" mb={1}>רקע לראיון (קונטקסט)</Text>
                 <Textarea
                    value={backgroundContext}
                    onChange={(e) => setBackgroundContext(e.target.value)}
                    placeholder="כתוב כאן רקע על המרואיין ומטרת הראיון..."
                    size="sm"
                    bg="white"
                    resize="vertical"
                    maxH="150px"
                    minH="80px"
                    fontSize="sm"
                 />
            </Box>

            <Flex p={3} justify="space-between" align="center" bg={cardBg} borderBottom="1px" borderColor={borderColor}>
                <Text fontWeight="bold" color="gray.600">פתקים ומחקר</Text>
                <Button
                    size="xs"
                    leftIcon={<AddIcon />}
                    colorScheme="blue"
                    variant="solid"
                    onClick={() => {
                        const newId = Math.random().toString(36).substr(2, 9)
                        setNotes([...notes, { id: newId, title: 'פתק חדש', type: 'bucket', items: [] }])
                        setSelectedNoteId(newId)
                    }}
                >
                    פתק חדש
                </Button>
            </Flex>
            <VStack p={3} spacing={3} overflowY="auto" flex="1" align="stretch" as={Reorder.Group} axis="y" values={notes} onReorder={setNotes}>
                {notes.map(note => (
                    <NoteItem
                        key={note.id}
                        note={note}
                        notes={notes}
                        setNotes={setNotes}
                        isSelected={selectedNoteId === note.id}
                        onSelect={() => setSelectedNoteId(note.id)}
                    />
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
                                    <Button
                                        size="xs"
                                        variant="outline"
                                        leftIcon={<AddIcon />}
                                        onClick={() => handleAddToNote({ type: 'text', content: res.snippet, title: res.title, domain: res.domain })}
                                    >
                                        הוסף לפתק
                                    </Button>
                                </HStack>
                            </Box>
                        ))}

                        {/* Image Results (Mock Grid) */}
                        <Text fontWeight="bold" fontSize="sm" color="gray.500" mt={2}>תמונות</Text>
                        <HStack spacing={2} overflowX="auto" pb={2}>
                            {searchResults.images.map((img) => (
                                <Box key={img.id} minW="100px" h="80px" bg="gray.200" borderRadius="md" position="relative" role="group">
                                    <Image
                                        src={img.src}
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
                                        <Button
                                            size="xs"
                                            colorScheme="whiteAlpha"
                                            variant="solid"
                                            onClick={() => handleAddToNote({ type: 'image', src: img.src, domain: img.domain })}
                                        >
                                            <AddIcon />
                                        </Button>
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
                                    value={block.text}
                                    onChange={(e) => updateOutlineBlock(block.id, e.target.value)}
                                    fontWeight="bold"
                                    fontSize="lg"
                                    variant="unstyled"
                                    placeholder="כותרת..."
                                />
                            ) : (
                                <Textarea
                                    value={block.text}
                                    onChange={(e) => updateOutlineBlock(block.id, e.target.value)}
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
                     <Box opacity={0.5} _hover={{ opacity: 1 }} cursor="pointer" onClick={addOutlineBlock}>
                        <Text>+ לחץ להוספת פסקה חדשה...</Text>
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
