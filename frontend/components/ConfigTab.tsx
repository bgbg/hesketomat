'use client'

import { useState, useRef } from 'react'
import {
  Box,
  Input,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Image,
  useToast,
  Spinner,
  Center,
  Text,
  Alert,
  AlertIcon,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure,
  ButtonGroup,
} from '@chakra-ui/react'
import useSWR from 'swr'
import { podcastsApi, type PodcastWithCount, type ValidateResponse } from '../lib/api'

export default function ConfigTab() {
  const [rssUrl, setRssUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [podcastToDelete, setPodcastToDelete] = useState<PodcastWithCount | null>(null)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const cancelRef = useRef<HTMLButtonElement>(null)
  const toast = useToast()

  const { data, error, isLoading: isLoadingPodcasts, mutate } = useSWR<PodcastWithCount[]>(
    '/podcasts/with_counts',
    () => podcastsApi.getAllWithCounts(),
    {
      onError: (err) => {
        console.error('SWR Error in ConfigTab:', err)
        toast({
          title: 'שגיאה',
          description: err.message || 'שגיאה בטעינת ההסכתים',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }
  )
  const podcasts = data || []

  const handleAddPodcast = async () => {
    if (!rssUrl) return

    try {
      setIsLoading(true)
      const validation = await podcastsApi.validate(rssUrl)
      if (validation.valid) {
        const podcast = validation.podcast
        await podcastsApi.add(podcast)
        toast({
          title: 'הסכת נוסף בהצלחה',
          description: `הסכת ${podcast.title} נוסף למערכת`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        })
        setRssUrl('')
        mutate()
      } else {
        toast({
          title: 'שגיאה',
          description: validation.error || 'לא ניתן להוסיף את ההסכת',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } catch (err) {
      console.error('Error adding podcast:', err)
      toast({
        title: 'שגיאה',
        description: err.message || 'שגיאה בהוספת ההסכת',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async (podcast: PodcastWithCount) => {
    try {
      await podcastsApi.refresh(podcast.id)
      toast({
        title: 'הסכת עודכן בהצלחה',
        description: `הסכת ${podcast.title} עודכן`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
      mutate()
    } catch (err) {
      console.error('Error refreshing podcast:', err)
      toast({
        title: 'שגיאה',
        description: err.message || 'שגיאה בעדכון ההסכת',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const handleDeleteClick = (podcast: PodcastWithCount) => {
    setPodcastToDelete(podcast)
    onOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!podcastToDelete) return

    try {
      await podcastsApi.delete(podcastToDelete.id)
      toast({
        title: 'הסכת נמחק בהצלחה',
        description: `הסכת ${podcastToDelete.title} נמחק`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
      setPodcastToDelete(null)
      onClose()
      mutate()
    } catch (err) {
      console.error('Error deleting podcast:', err)
      toast({
        title: 'שגיאה',
        description: err.message || 'שגיאה במחיקת ההסכת',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  return (
    <Box>
      <Box mb={4}>
        <Input
          placeholder="הכנס כתובת RSS"
          value={rssUrl}
          onChange={(e) => setRssUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddPodcast()}
          mb={2}
        />
        <Button
          colorScheme="blue"
          onClick={handleAddPodcast}
          isLoading={isLoading}
        >
          הוסף הסכת
        </Button>
      </Box>

      {error ? (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error.message || 'שגיאה בטעינת ההסכתים'}
        </Alert>
      ) : isLoadingPodcasts ? (
        <Center>
          <Spinner />
        </Center>
      ) : podcasts.length === 0 ? (
        <Center>
          <Text>אין הסכתים</Text>
        </Center>
      ) : (
        <Table>
          <Thead>
            <Tr>
              <Th>תמונה</Th>
              <Th>כותרת</Th>
              <Th>תיאור</Th>
              <Th>כתובת RSS</Th>
              <Th>עדכון אחרון</Th>
              <Th>פרקים</Th>
              <Th>פעולות</Th>
            </Tr>
          </Thead>
          <Tbody>
            {podcasts.map((podcast) => (
              <Tr key={podcast.id}>
                <Td verticalAlign="top">
                  {podcast.image_url && (
                    podcast.homepage_url ? (
                      <a href={podcast.homepage_url} target="_blank" rel="noopener noreferrer">
                        <Image
                          src={podcast.image_url}
                          alt={podcast.title}
                          height="60px"
                          objectFit="contain"
                          cursor="pointer"
                        />
                      </a>
                    ) : (
                      <Image
                        src={podcast.image_url}
                        alt={podcast.title}
                        height="60px"
                        objectFit="contain"
                      />
                    )
                  )}
                </Td>
                <Td verticalAlign="top">
                  {podcast.homepage_url ? (
                    <a href={podcast.homepage_url} target="_blank" rel="noopener noreferrer">
                      <Text cursor="pointer" color="blue.500" _hover={{ textDecoration: 'underline' }}>
                        {podcast.title}
                      </Text>
                    </a>
                  ) : (
                    podcast.title
                  )}
                </Td>
                <Td verticalAlign="top">{podcast.description}</Td>
                <Td verticalAlign="top">{podcast.rss_url}</Td>
                <Td verticalAlign="top">
                  {podcast.last_updated
                    ? new Date(podcast.last_updated).toLocaleString('he-IL')
                    : 'מעולם לא'}
                </Td>
                <Td verticalAlign="top">
                  {podcast.episode_count}
                </Td>
                <Td verticalAlign="top">
                  <ButtonGroup size="sm" spacing={2}>
                    <Button
                      colorScheme="blue"
                      onClick={() => handleRefresh(podcast)}
                    >
                      רענן
                    </Button>
                    <Button
                      colorScheme="red"
                      onClick={() => handleDeleteClick(podcast)}
                    >
                      הסר
                    </Button>
                  </ButtonGroup>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              מחיקת הסכת
            </AlertDialogHeader>

            <AlertDialogBody>
              האם אתה בטוח שברצונך למחוק את ההסכת "{podcastToDelete?.title}"?
              כל הפרקים המשויכים להסכת זה יימחקו גם כן.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                ביטול
              </Button>
              <Button colorScheme="red" onClick={handleDeleteConfirm} mr={3}>
                מחק
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  )
}